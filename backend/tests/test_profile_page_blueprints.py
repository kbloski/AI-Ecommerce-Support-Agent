import json
import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from api.routes.general_routes import register_general_routes
from application.assemblers.page_blueprint_assembler import PageBlueprintAssembler
from application.handlers.page_blueprint import create_page_blueprint_handler as creation
from application.handlers.page_blueprint import generate_page_blueprint_handler as generation
from application.handlers.page_blueprint import update_page_blueprint_handler as editing
from application.services.page_blueprint_service import PageBlueprintService
from domain.models import models
from domain.models.page.page_blueprint import PageBlueprint
from domain.enums.page_type import PageType
from infrastructure.database.db import Base
from infrastructure.database.page_blueprints_migration import migrate_page_blueprints_to_profiles
from infrastructure.database.page_blueprint_sections_migration import migrate_page_blueprint_sections
from infrastructure.repositories.page_blueprint_repository import PageBlueprintRepository
from infrastructure.repositories.page_blueprint_sections_repository import PageBlueprintSectionsRepository
from application.dtos.page_blueprint.page_blueprint_fields import GeneratePageBlueprintRequest
from application.services.llm_result_validation import LlmGenerationError
from fastapi import HTTPException
from pydantic import ValidationError


def sqlite_engine():
    engine = create_engine("sqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    return engine


class ProfilePageBlueprintTests(unittest.TestCase):
    def setUp(self):
        self.engine = sqlite_engine()
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.addCleanup(self.db.close)
        self.db.execute(text("INSERT INTO offers_raw (id, name) VALUES (1, 'Offer')"))
        self.db.execute(text("INSERT INTO offer_sources (id, offer_id, offer_details) VALUES (1, 1, 'Facts')"))
        self.db.execute(text("INSERT INTO offer_profiles (id, offer_source_id, name) VALUES (1, 1, 'Profile'), (2, 1, 'Other')"))
        self.db.commit()
        self.repo = PageBlueprintRepository(Mock(), self.db)
        self.sections_repo = PageBlueprintSectionsRepository(Mock(), self.db)
        self.catalog = [{"id": "hero"}, {"id": "faq"}]
        self.sections = SimpleNamespace(get_all=lambda: self.catalog, get_allowed_ids=lambda: {"hero", "faq"}, get_all_for_blueprints=lambda: self.catalog)
        self.service = PageBlueprintService(Mock(), self.repo, PageBlueprintAssembler(Mock(), self.sections_repo))
        self.profile_service = Mock()
        self.composer = Mock()
        self.composer.compose.return_value = "PROFILE AND FACTUAL OFFER CONTEXT"
        self.ai = Mock()
        self.container = SimpleNamespace(
            db=lambda: self.db, offer_profile_service=lambda: self.profile_service,
            page_blueprint_repository=lambda: self.repo, page_blueprint_service=lambda: self.service,
            page_blueprint_sections_repository=lambda: self.sections_repo,
            page_sections_service=lambda: self.sections, llm_context_composer=lambda: self.composer,
            ai_service=lambda: self.ai,
        )
        stack = ExitStack()
        self.addCleanup(stack.close)
        for module in (creation, editing, generation):
            stack.enter_context(patch.object(module, "Container", lambda: self.container))

    def create(self):
        return creation.create_page_blueprint_handler(1, "Blueprint", [
            {"type": "hero", "name": "First hero", "purpose": "Introduce offer", "position": 1},
            {"type": "hero", "name": "Second hero", "purpose": "Reinforce value", "position": 2, "is_optional": True},
            {"type": "custom_type", "name": "Custom", "purpose": "Explain usage", "position": 3},
        ], description="Page approach")

    def test_create_edit_list_and_delete_preserve_repeated_types_ids_and_profile_ownership(self):
        created = self.create()
        self.assertEqual(created.offer_profile_id, 1)
        self.assertEqual(len(created.sections), 3)
        self.assertEqual([s["type"] for s in created.sections], ["hero", "hero", "custom_type"])
        self.assertEqual(created.description, "Page approach")
        self.assertEqual(self.service.get_page_blueprint_by_offer_profile(2), [])
        old_id = created.sections[1]["id"]
        updated = editing.update_page_blueprint_handler(created.id, "Updated", [
            {**created.sections[1], "position": 1},
            {"type": "hero", "name": "Another", "purpose": "New section", "position": 2},
        ])
        self.assertEqual(updated.sections[0]["id"], old_id)
        self.assertEqual([s["type"] for s in updated.sections], ["hero", "hero"])
        self.assertTrue(updated.sections[0]["is_optional"])
        self.assertEqual(len(updated.sections), 2)
        self.assertTrue(self.repo.delete(created.id))
        self.assertEqual(self.sections_repo.find_for_blueprint(created.id), [])

    def test_failed_section_write_rolls_back_entire_blueprint(self):
        with patch.object(self.sections_repo, "create_many", side_effect=RuntimeError("write failed")):
            with self.assertRaises(RuntimeError):
                self.create()
        self.assertEqual(self.db.query(PageBlueprint).count(), 0)

    def test_cannot_take_a_section_from_another_blueprint(self):
        first, second = self.create(), self.create()
        with self.assertRaises(HTTPException) as error:
            editing.update_page_blueprint_handler(first.id, "Changed", [{**second.sections[0], "position": 1}])
        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(self.service.get_page_blueprint_by_id(first.id).name, "Blueprint")
        self.assertEqual(len(self.service.get_page_blueprint_by_id(second.id).sections), 3)

    def test_generation_uses_section_count_instructions_and_accepts_custom_repeated_types(self):
        payload = {"name": "Generated", "description": "Approach", "sections": [
            {"type": "custom_type", "name": "First", "purpose": "Introduce", "position": 1},
            {"type": "custom_type", "name": "Second", "purpose": "Explain", "position": 2},
        ]}
        self.ai.chat_llm.return_value = SimpleNamespace(content=json.dumps(payload))
        request = GeneratePageBlueprintRequest(section_count=2, generation_instructions="Focus on product usage")
        result = generation.generate_page_blueprint_handler(1, request)
        self.assertEqual(result.offer_profile_id, 1)
        self.assertEqual(len(result.sections), 2)
        self.assertEqual(self.db.query(PageBlueprint).count(), 1)
        context_args = self.composer.compose.call_args.kwargs
        self.assertEqual(context_args["root"].id, 1)
        self.assertEqual(context_args["root"].type.value, "offer_profile")
        data = json.loads(self.ai.chat_llm.call_args.kwargs["messages"][1].content)
        self.assertIsNone(data["page_type"])
        self.assertNotIn("section_suggestions", data)
        self.assertEqual(data["requested_section_count"], 2)
        self.assertEqual(data["generation_instructions"], "Focus on product usage")
        # No catalog is required for generation.
        self.catalog.clear()
        generation.generate_page_blueprint_handler(1, request)
        self.assertEqual(self.db.query(PageBlueprint).count(), 2)

    def test_only_product_page_receives_section_suggestions(self):
        self.ai.chat_llm.return_value = SimpleNamespace(content=json.dumps({
            "name": "Generated", "sections": [
                {"type": "hero", "name": "Opening", "purpose": "Introduce", "position": 1},
            ],
        }))
        generation.generate_page_blueprint_handler(1, GeneratePageBlueprintRequest(section_count=1))
        data = json.loads(self.ai.chat_llm.call_args.kwargs["messages"][1].content)
        self.assertIsNone(data["page_type"])
        self.assertNotIn("section_suggestions", data)
        generation.generate_page_blueprint_handler(1, GeneratePageBlueprintRequest(page_type="product_page", section_count=1))
        data = json.loads(self.ai.chat_llm.call_args.kwargs["messages"][1].content)
        self.assertEqual(data["section_suggestions"], self.catalog)

    def test_wrong_count_and_invalid_order_do_not_save_partial_blueprints(self):
        section = {"type": "hero", "name": "Hero", "purpose": "Introduce", "position": 1}
        for sections in ([section], [section, section], [{**section, "position": 2}, {**section, "position": 3}]):
            with self.subTest(sections=sections):
                self.ai.chat_llm.return_value = SimpleNamespace(content=json.dumps({"name": "Invalid", "sections": sections}))
                with self.assertRaises(LlmGenerationError):
                    generation.generate_page_blueprint_handler(1, GeneratePageBlueprintRequest(section_count=2))
        self.assertEqual(self.db.query(PageBlueprint).count(), 0)

    def test_generation_without_section_count_lets_ai_choose_and_validates_order(self):
        request = GeneratePageBlueprintRequest(section_count=None, generation_instructions="Short page")
        self.ai.chat_llm.return_value = SimpleNamespace(content=json.dumps({
            "name": "AI choice", "sections": [
                {"type": "hero", "name": "Opening", "purpose": "Introduce", "position": 1},
                {"type": "faq", "name": "Questions", "purpose": "Resolve doubts", "position": 2},
            ],
        }))
        result = generation.generate_page_blueprint_handler(1, request)
        self.assertEqual(len(result.sections), 2)
        data = json.loads(self.ai.chat_llm.call_args.kwargs["messages"][1].content)
        self.assertIsNone(data["requested_section_count"])
        self.assertIn("Otherwise, choose an appropriate count", self.ai.chat_llm.call_args.kwargs["messages"][0].content)

        self.ai.chat_llm.return_value = SimpleNamespace(content=json.dumps({
            "name": "Bad order", "sections": [
                {"type": "hero", "name": "Opening", "purpose": "Introduce", "position": 2},
            ],
        }))
        with self.assertRaises(LlmGenerationError):
            generation.generate_page_blueprint_handler(1, request)
        self.assertEqual(self.db.query(PageBlueprint).count(), 1)

    def test_generation_request_limits(self):
        self.assertIsNone(GeneratePageBlueprintRequest().page_type)
        self.assertIs(GeneratePageBlueprintRequest(page_type="product_page").page_type, PageType.PRODUCT_PAGE)
        for values in ({"section_count": 0}, {"section_count": 51}, {"section_count": True}, {"page_type": "unknown"}, {"generation_instructions": "x" * 4001}):
            with self.subTest(values=values), self.assertRaises(ValidationError):
                GeneratePageBlueprintRequest(**values)

    def test_http_create_update_and_generate_contracts(self):
        router = APIRouter()
        register_general_routes(router)
        app = FastAPI()
        app.include_router(router)
        with TestClient(app) as client:
            fields = {"name": "HTTP blueprint", "description": "Approach", "sections": [
                {"type": "custom", "name": "First", "purpose": "Introduce", "position": 1},
                {"type": "custom", "name": "Second", "purpose": "Explain", "position": 2},
            ]}
            created = client.post("/offer-profiles/1/page-blueprints/create", json=fields)
            self.assertEqual(created.status_code, 200, created.text)
            saved = created.json()
            self.assertEqual([section["type"] for section in saved["sections"]], ["custom", "custom"])
            fields["sections"] = [{**saved["sections"][1], "position": 1}]
            updated = client.post(f"/page-blueprints/{saved['id']}/update", json=fields)
            self.assertEqual(updated.status_code, 200, updated.text)
            self.assertEqual(updated.json()["sections"][0]["id"], saved["sections"][1]["id"])
            invalid = client.post("/offer-profiles/1/page-blueprints/generate", json={"section_count": 0})
            self.assertEqual(invalid.status_code, 422)
            invalid_type = client.post("/offer-profiles/1/page-blueprints/generate", json={"page_type": "unknown"})
            self.assertEqual(invalid_type.status_code, 422)
            self.ai.chat_llm.return_value = SimpleNamespace(content=json.dumps({
                "name": "Generated over HTTP", "sections": [
                    {"type": "custom", "name": "Single", "purpose": "Explain", "position": 1},
                ],
            }))
            generated = client.post("/offer-profiles/1/page-blueprints/generate", json={
                "page_type": "product_page", "section_count": 1, "generation_instructions": "Use one section",
            })
            self.assertEqual(generated.status_code, 200, generated.text)
            self.assertEqual(len(generated.json()["sections"]), 1)
            self.assertEqual(json.loads(self.ai.chat_llm.call_args.kwargs["messages"][1].content)["section_suggestions"], self.catalog)
            unspecified = client.post("/offer-profiles/1/page-blueprints/generate", json={"section_count": None})
            self.assertEqual(unspecified.status_code, 200, unspecified.text)
            self.assertEqual(len(unspecified.json()["sections"]), 1)

    def test_routes_expose_profile_blueprints_and_remove_old_outputs(self):
        router = APIRouter()
        register_general_routes(router)
        paths = {route.path for route in router.routes}
        self.assertIn("/offer-profiles/{offer_profile_id}/page-blueprints", paths)
        self.assertIn("/offer-profiles/{offer_profile_id}/page-blueprints/create", paths)
        self.assertIn("/offer-profiles/{offer_profile_id}/page-blueprints/generate", paths)
        self.assertIn("/page-blueprints/{id}/update", paths)
        self.assertFalse(any(part in path for path in paths for part in ("page-requirements", "page-content-plan", "page-copy", "/page-blueprint/")))


class PageBlueprintMigrationTests(unittest.TestCase):
    def setUp(self):
        self.engine = sqlite_engine()
        self.addCleanup(self.engine.dispose)
        with self.engine.begin() as conn:
            for ddl in (
                "CREATE TABLE offers_raw (id INTEGER PRIMARY KEY, name VARCHAR)",
                "CREATE TABLE offer_sources (id INTEGER PRIMARY KEY, offer_id INTEGER REFERENCES offers_raw(id))",
                "CREATE TABLE offer_profiles (id INTEGER PRIMARY KEY, offer_source_id INTEGER REFERENCES offer_sources(id), name VARCHAR NOT NULL, created_at DATETIME)",
                "CREATE TABLE brand_marketing (id INTEGER PRIMARY KEY, offer_source_id INTEGER REFERENCES offer_sources(id))",
                "CREATE TABLE marketing_strategy (id INTEGER PRIMARY KEY, brand_marketing_id INTEGER REFERENCES brand_marketing(id))",
                "CREATE TABLE offer_strategy (id INTEGER PRIMARY KEY, marketing_strategy_id INTEGER REFERENCES marketing_strategy(id))",
                "CREATE TABLE message_strategy (id INTEGER PRIMARY KEY, offer_strategy_id INTEGER REFERENCES offer_strategy(id))",
                "CREATE TABLE page_strategy (id INTEGER PRIMARY KEY, message_strategy_id INTEGER REFERENCES message_strategy(id))",
                "CREATE TABLE page_requirements (id INTEGER PRIMARY KEY, page_strategy_id INTEGER REFERENCES page_strategy(id), name VARCHAR, is_favorite BOOLEAN, created_at DATETIME, updated_at DATETIME)",
                "CREATE TABLE page_section_requirement (id INTEGER PRIMARY KEY, page_requirements_id INTEGER REFERENCES page_requirements(id), page_section_type_id VARCHAR, requirement_type VARCHAR, position INTEGER)",
                "CREATE TABLE page_blueprint (id INTEGER PRIMARY KEY, page_requirements_id INTEGER REFERENCES page_requirements(id), sections JSON)",
                "CREATE TABLE page_content_plan (id INTEGER PRIMARY KEY, page_blueprint_id INTEGER REFERENCES page_blueprint(id))",
                "CREATE TABLE page_copy (id INTEGER PRIMARY KEY, page_content_plan_id INTEGER REFERENCES page_content_plan(id))",
            ):
                conn.execute(text(ddl))
            conn.execute(text("INSERT INTO offers_raw VALUES (1, 'Existing offer')"))
            for table in ("offer_sources", "brand_marketing", "marketing_strategy", "offer_strategy", "message_strategy", "page_strategy"):
                conn.execute(text(f"INSERT INTO {table} VALUES (1, 1)"))
            conn.execute(text("INSERT INTO offer_profiles VALUES (10, 1, 'Profile', CURRENT_TIMESTAMP)"))
            conn.execute(text("INSERT INTO page_requirements VALUES (42, 1, 'Existing selection', 1, '2025-01-01', '2025-02-01')"))
            conn.execute(text("INSERT INTO page_section_requirement VALUES (7, 42, 'hero', 'required', 1), (8, 42, 'faq', 'excluded', NULL)"))
            conn.execute(text("INSERT INTO page_blueprint VALUES (88, 42, '[]')"))
            conn.execute(text("INSERT INTO page_content_plan VALUES (9, 88)"))
            conn.execute(text("INSERT INTO page_copy VALUES (5, 9)"))

    def test_migration_preserves_requirements_and_discards_old_blueprints_and_downstream(self):
        migrate_page_blueprints_to_profiles(self.engine)
        migrate_page_blueprints_to_profiles(self.engine)
        tables = set(inspect(self.engine).get_table_names())
        self.assertTrue(tables.isdisjoint({"page_requirements", "page_content_plan", "page_copy"}))
        with self.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT id, offer_profile_id, name, is_favorite, created_at FROM page_blueprint")).one(), (42, 10, "Existing selection", 1, "2025-01-01"))
            self.assertEqual(conn.execute(text("SELECT id, page_blueprint_id, page_section_type_id, requirement_type, position FROM page_section_requirement ORDER BY id")).all(), [(7, 42, "hero", "required", 1), (8, 42, "faq", "excluded", None)])
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_key_check").all(), [])
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)

    def test_new_sections_migration_preserves_ids_optional_status_and_order(self):
        migrate_page_blueprints_to_profiles(self.engine)
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO page_section_requirement (id, page_blueprint_id, page_section_type_id, requirement_type, position) VALUES (9, 42, 'hero', 'optional', 3)"))
        migrate_page_blueprint_sections(self.engine)
        migrate_page_blueprint_sections(self.engine)
        self.assertNotIn("page_section_requirement", inspect(self.engine).get_table_names())
        with self.engine.connect() as conn:
            sections = conn.execute(text("SELECT id, page_blueprint_id, type, name, position, is_optional FROM page_blueprint_sections ORDER BY position")).all()
            self.assertEqual(sections, [(7, 42, "hero", "Hero", 1, 0), (9, 42, "hero", "Hero", 2, 1)])
            self.assertEqual(conn.execute(text("SELECT name, description FROM page_blueprint")).one(), ("Existing selection", ""))
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_key_check").all(), [])

    def test_sections_migration_conflict_does_not_overwrite_existing_data(self):
        migrate_page_blueprints_to_profiles(self.engine)
        migrate_page_blueprint_sections(self.engine)
        with self.engine.begin() as conn:
            conn.execute(text("CREATE TABLE page_section_requirement (id INTEGER PRIMARY KEY)"))
        with self.assertRaises(RuntimeError):
            migrate_page_blueprint_sections(self.engine)
        with self.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT COUNT(*) FROM page_blueprint_sections")).scalar(), 1)
        self.assertIn("page_section_requirement", inspect(self.engine).get_table_names())

    def test_ambiguous_profiles_preserve_data_under_a_dedicated_profile(self):
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO offer_profiles VALUES (11, 1, 'Other profile', CURRENT_TIMESTAMP)"))
        migrate_page_blueprints_to_profiles(self.engine)
        with self.engine.connect() as conn:
            owner = conn.execute(text("SELECT offer_profile_id FROM page_blueprint WHERE id=42")).scalar()
            self.assertNotIn(owner, (10, 11))
            self.assertEqual(conn.execute(text("SELECT offer_source_id FROM offer_profiles WHERE id=:id"), {"id": owner}).scalar(), 1)

    def test_unresolved_owner_rolls_back_before_retiring_output_data(self):
        with self.engine.begin() as conn:
            conn.execute(text("UPDATE brand_marketing SET offer_source_id=NULL"))
        with self.assertRaises(RuntimeError):
            migrate_page_blueprints_to_profiles(self.engine)
        with self.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT COUNT(*) FROM page_copy")).scalar(), 1)
            self.assertEqual(conn.execute(text("SELECT COUNT(*) FROM page_requirements")).scalar(), 1)
            self.assertEqual(conn.execute(text("SELECT id FROM page_blueprint")).scalar(), 88)
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)

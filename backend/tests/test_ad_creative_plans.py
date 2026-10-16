import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session

from api.routes import ad_creative_plans_routes as routes
from application.dtos.ad_creative_plans.creative_plan_fields import (
    CreateCreativePlanRequest, GenerateCreativePlansRequest, UpdateCreativePlanRequest,
)
from application.handlers.ad_creative_plans import creative_plan_handlers as handlers
from application.handlers.ad_creative_plans import generate_ad_creative_plans_handler as generation
from application.services.ad_concept_service import AdConceptService
from application.services.llm_context_composer import LlmContextComposer
from domain.models import models
from domain.models.ad.ad_concept import AdConcept
from domain.models.ad.ad_creative_plan import AdCreativePlan
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource
from domain.models.offer.offer_profile import OfferProfile
from infrastructure.database.db import Base
from infrastructure.database import init_db as migrations
from infrastructure.repositories.ad_concepts_repository import AdConceptsRepository
from infrastructure.repositories.ad_creative_plans_repository import AdCreativePlansRepository
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository
from infrastructure.repositories.ad_frameworks_repository import AdFrameworksRepository
from infrastructure.services.path_service import PathService


class CreativePlanTests(unittest.TestCase):
    FIELDS = {"name": "Demo sequence", "description": "Show the service in action",
              "format": "video", "plan": "SCENE 1 (0-5s): Show the process.\nSCENE 2 (5-10s): Show the CTA."}

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add(OfferRaw(id=1, name="Service"))
        self.db.flush()
        self.db.add(OfferSource(id=1, offer_id=1, offer_details="Source facts"))
        self.db.flush()
        self.db.add_all([OfferProfile(id=1, offer_source_id=1, name="Profile"), OfferProfile(id=2, offer_source_id=1, name="Foreign profile")])
        self.db.flush()
        for id, profile_id, name in [(1, 1, "Selected concept"), (2, 2, "Foreign concept"), (3, 1, "Unselected concept")]:
            self.db.add(AdConcept(id=id, offer_profile_id=profile_id, name=name, description="Concept description", format="video", core_idea="Demonstration", key_message="How it works", generation_mode="standard"))
        self.db.commit()
        self.repo = AdCreativePlansRepository(None, self.db)
        self.frameworks = AdFrameworksRepository(None, PathService(None))
        concepts = AdConceptsRepository(None, self.db)
        composer = LlmContextComposer(
            SimpleNamespace(build_llm_context=lambda id: "<offer_profile>Profile</offer_profile>",
                            get_offer_profile_details_by_id=lambda id: SimpleNamespace(offer_source_id=1)),
            None, None,
            SimpleNamespace(build_llm_context=lambda id: "<offer_source>Source facts</offer_source>"),
            None, AdConceptService(concepts),
        )
        self.ai = Mock()
        self.ai.chat_json.return_value = {"plans": [self.FIELDS.copy()]}
        container = SimpleNamespace(
            offer_profiles_repository=lambda: OfferProfilesRepository(None, self.db),
            ad_concepts_repository=lambda: concepts,
            ad_creative_plans_repository=lambda: self.repo,
            ad_frameworks_repository=lambda: self.frameworks,
            llm_context_composer=lambda: composer, ai_service=lambda: self.ai,
        )
        for module in (handlers, generation):
            patcher = patch.object(module, "Container", lambda: container)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.engine.dispose)
        self.addCleanup(self.db.close)

    def test_generation_uses_selected_concept_source_and_instructions(self):
        result = routes.generate_creative_plans(1, GenerateCreativePlansRequest(ad_concept_id=1, generation_instructions="No voiceover"))
        self.assertEqual(result[0]["ad_concept_id"], 1)
        self.assertEqual(result[0]["offer_profile_id"], 1)
        self.assertEqual(result[0]["plan"], self.FIELDS["plan"])
        self.assertFalse(result[0]["is_reviewed"])
        call = self.ai.chat_json.call_args
        content = call.kwargs["messages"][1].content
        for required in ("Selected concept", "Source facts", "<offer_profile>", "No voiceover"):
            self.assertIn(required, content)
        for excluded in ("Foreign concept", "Unselected concept"):
            self.assertNotIn(excluded, content)
        self.assertNotIn("rule_sets", call.kwargs)  # Preserve chat_json language defaults.

    def test_without_concept_and_image_format(self):
        self.ai.chat_json.return_value = {"plans": [{**self.FIELDS, "format": "image"}]}
        result = routes.generate_creative_plans(1, GenerateCreativePlansRequest(preferred_format="image"))
        self.assertEqual(result[0]["format"], "image")
        self.assertIs(type(self.repo.get_by_id(result[0]["id"]).format), str)
        self.assertIsNone(result[0]["ad_concept_id"])
        self.assertNotIn("<ad_concepts", self.ai.chat_json.call_args.kwargs["messages"][1].content)

    def test_explicit_format_can_override_concept_format(self):
        self.ai.chat_json.return_value = {"plans": [{**self.FIELDS, "format": "image"}]}
        result = routes.generate_creative_plans(1, GenerateCreativePlansRequest(ad_concept_id=1, preferred_format="image"))
        self.assertEqual(result[0]["format"], "image")

    def test_selected_framework_from_file_is_in_generation_context(self):
        framework = self.frameworks.get_by_id("product_demo")
        result = routes.generate_creative_plans(1, GenerateCreativePlansRequest(ad_framework_id=framework.id))
        self.assertEqual(result[0]["format"], framework.format)
        content = self.ai.chat_json.call_args.kwargs["messages"][1].content
        self.assertIn(framework.name, content)
        self.assertIn(framework.rules[0], content)
        self.assertIn(framework.structure[0]["purpose"], content)

    def test_missing_and_incompatible_frameworks_are_rejected_before_ai(self):
        for framework_id, preferred_format, code in [("missing-framework", None, 404), ("product_demo", "image", 422)]:
            with self.assertRaises(HTTPException) as error:
                routes.generate_creative_plans(1, GenerateCreativePlansRequest(ad_framework_id=framework_id, preferred_format=preferred_format))
            self.assertEqual(error.exception.status_code, code)
        self.ai.chat_json.assert_not_called()

    def test_framework_format_overrides_concept_default(self):
        framework = self.frameworks.get_by_id("product_demo")
        self.db.get(AdConcept, 1).format = "image"
        self.db.commit()
        result = routes.generate_creative_plans(1, GenerateCreativePlansRequest(ad_concept_id=1, ad_framework_id=framework.id))
        self.assertEqual(result[0]["format"], "video")

    def test_foreign_or_missing_concept_is_rejected_before_ai(self):
        for id, code in [(2, 422), (999, 404)]:
            with self.assertRaises(HTTPException) as error:
                routes.generate_creative_plans(1, GenerateCreativePlansRequest(ad_concept_id=id))
            self.assertEqual(error.exception.status_code, code)
        self.ai.chat_json.assert_not_called()
        self.assertEqual(self.db.query(AdCreativePlan).count(), 0)

    def test_invalid_ai_output_never_saves_partial_batch(self):
        for invalid in (
            {"plans": [self.FIELDS, {**self.FIELDS, "plan": {"scene": "nested"}}]},
            {"plans": [{**self.FIELDS, "plan": "   "}, self.FIELDS]},
            {"plans": [{**self.FIELDS, "is_reviewed": True}, self.FIELDS]},
            {"plans": [self.FIELDS]},
            {"plans": [self.FIELDS, {**self.FIELDS, "format": "image"}]},
            {"plans": [{**self.FIELDS, "format": "audio"}, self.FIELDS]},
        ):
            with self.subTest(response=invalid):
                self.ai.chat_json.return_value = invalid
                with self.assertRaises(HTTPException) as error:
                    routes.generate_creative_plans(1, GenerateCreativePlansRequest(count=2, preferred_format="video"))
                self.assertEqual(error.exception.status_code, 502)
                self.assertEqual(self.db.query(AdCreativePlan).count(), 0)

    def test_create_update_review_list_and_delete(self):
        created = routes.create_creative_plan(1, CreateCreativePlanRequest(**self.FIELDS, ad_concept_id=1))
        request = UpdateCreativePlanRequest(**self.FIELDS, ad_concept_id=1, is_reviewed=True)
        self.assertTrue(routes.update_creative_plan(created["id"], request)["is_reviewed"])
        edited = routes.update_creative_plan(created["id"], request.model_copy(update={"plan": "Changed production plan"}))
        self.assertFalse(edited["is_reviewed"])
        self.assertEqual(len(routes.list_creative_plans(1)), 1)
        self.assertEqual(routes.list_creative_plans(2), [])
        with self.assertRaises(HTTPException):
            routes.update_creative_plan(created["id"], request.model_copy(update={"ad_concept_id": 2}))
        self.db.refresh(self.repo.get_by_id(created["id"]))
        self.assertEqual(self.repo.get_by_id(created["id"]).ad_concept_id, 1)
        self.assertTrue(routes.delete_creative_plan(created["id"])["deleted"])
        self.assertEqual(routes.list_creative_plans(1), [])

    def test_concept_deletion_preserves_plan_and_profile_deletion_cascades(self):
        created = routes.create_creative_plan(1, CreateCreativePlanRequest(**self.FIELDS, ad_concept_id=1))
        self.db.execute(text("DELETE FROM ad_concepts WHERE id=1"))
        self.db.commit()
        self.db.expire_all()
        item = self.repo.get_by_id(created["id"])
        self.assertIsNone(item.ad_concept_id)
        self.assertEqual(item.plan, self.FIELDS["plan"])
        self.db.execute(text("DELETE FROM offer_profiles WHERE id=1"))
        self.db.commit()
        self.assertEqual(self.db.query(AdCreativePlan).count(), 0)

    def test_missing_profiles_and_plans(self):
        for action in (
            lambda: routes.list_creative_plans(999),
            lambda: routes.create_creative_plan(999, CreateCreativePlanRequest(**self.FIELDS)),
            lambda: routes.generate_creative_plans(999, GenerateCreativePlansRequest()),
            lambda: routes.update_creative_plan(999, UpdateCreativePlanRequest(**self.FIELDS)),
            lambda: routes.delete_creative_plan(999),
        ):
            with self.assertRaises(HTTPException) as error:
                action()
            self.assertEqual(error.exception.status_code, 404)

    def test_request_validation(self):
        for values in ({"count": 0}, {"count": 11}, {"ad_concept_id": 0}, {"preferred_format": ""}, {"preferred_format": "audio"}, {"generation_instructions": "x" * 4001}):
            with self.assertRaises(ValidationError):
                GenerateCreativePlansRequest(**values)

    def test_startup_creates_table_and_is_repeatable(self):
        self.db.close()
        with patch.object(migrations, "engine", self.engine):
            migrations.init_db()
            migrations.init_db()
        columns = {column["name"] for column in inspect(self.engine).get_columns("ad_creative_plans")}
        self.assertTrue({"id", "offer_profile_id", "ad_concept_id", "name", "description", "format", "plan", "is_reviewed"} <= columns)

    def test_http_generate_and_update_contract(self):
        # Avoid using a SQLite in-memory session from another TestClient thread.
        app = FastAPI()
        app.include_router(routes.router)
        with patch.object(routes, "generate_ad_creative_plans_handler", return_value=[{"id": 1}]) as generate:
            with TestClient(app) as client:
                response = client.post("/offer-profiles/1/creative-plans/generate", json={"ad_concept_id": 1, "generation_instructions": "No voiceover"})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), [{"id": 1}])
                self.assertEqual(generate.call_args.args[1].ad_concept_id, 1)
                self.assertEqual(client.post("/offer-profiles/1/creative-plans/generate", json={"count": 0}).status_code, 422)

    def seed_legacy_plan_table(self):
        self.db.close()
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE ad_creative_plans"))
            conn.execute(text("""
                CREATE TABLE ad_creative_plans (
                    id INTEGER PRIMARY KEY, offer_profile_id INTEGER NOT NULL
                        REFERENCES offer_profiles(id) ON DELETE CASCADE,
                    ad_concept_id INTEGER REFERENCES ad_concepts(id) ON DELETE SET NULL,
                    name VARCHAR(255) NOT NULL, description TEXT NOT NULL,
                    sections JSON NOT NULL, is_reviewed BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_favorite BOOLEAN NOT NULL DEFAULT 0
                )
            """))
            conn.execute(text("""
                INSERT INTO ad_creative_plans
                    (id, offer_profile_id, ad_concept_id, name, description, sections, is_reviewed, is_favorite)
                VALUES (5, 1, 1, 'Legacy plan', 'Existing plan', :sections, 1, 1)
            """), {"sections": '[{"name":"Opening", "text":"Keep this scene", "duration":5}]'})

    def test_legacy_sections_migrate_and_list_and_generate_work(self):
        from infrastructure.database.creative_plans_migration import migrate_creative_plan_content
        self.seed_legacy_plan_table()
        with patch.object(migrations, "engine", self.engine):
            migrations.init_db()
            migrations.init_db()
        result = routes.list_creative_plans(1)
        self.assertEqual(result[0]["id"], 5)
        self.assertEqual(result[0]["format"], "video")
        self.assertIn("Keep this scene", result[0]["plan"])
        self.assertIn('"duration": 5', result[0]["plan"])
        self.assertFalse(result[0]["is_reviewed"])
        columns = {column["name"] for column in inspect(self.engine).get_columns("ad_creative_plans")}
        self.assertNotIn("sections", columns)
        self.assertTrue({"format", "plan"} <= columns)
        with self.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT is_favorite FROM ad_creative_plans WHERE id=5")).scalar(), 1)
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)
            self.assertFalse(conn.exec_driver_sql("PRAGMA foreign_key_check").all())
        generated = routes.generate_creative_plans(1, GenerateCreativePlansRequest(ad_concept_id=1))
        self.assertGreater(generated[0]["id"], 5)
        self.assertEqual(len(routes.list_creative_plans(1)), 2)

    def test_legacy_migration_failure_rolls_back_and_restores_foreign_keys(self):
        from infrastructure.database.creative_plans_migration import migrate_creative_plan_content
        self.seed_legacy_plan_table()
        with self.engine.begin() as conn:
            conn.execute(text("CREATE TABLE ad_creative_plans_migrated (id INTEGER)"))
        with self.assertRaises(Exception):
            migrate_creative_plan_content(self.engine)
        with self.engine.connect() as conn:
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)
            self.assertIn("Keep this scene", conn.execute(text("SELECT sections FROM ad_creative_plans WHERE id=5")).scalar())

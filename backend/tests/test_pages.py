import json
import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from api.routes.general_routes import register_general_routes
from application.assemblers.page_blueprint_assembler import PageBlueprintAssembler
from application.dtos.page.page_fields import GeneratePageRequest
from application.handlers.page import generate_page_handler as generation
from application.handlers.page import get_pages_handler as retrieval
from application.services.llm_result_validation import LlmGenerationError
from application.services.page_blueprint_service import PageBlueprintService
from application.services.page_service import PageService
from domain.models import models
from domain.models.page.page import Page
from infrastructure.database.db import Base
from infrastructure.repositories.page_blueprint_repository import PageBlueprintRepository
from infrastructure.repositories.page_blueprint_sections_repository import PageBlueprintSectionsRepository
from infrastructure.repositories.page_repository import PageRepository


class PageGenerationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})
        self.addCleanup(self.engine.dispose)

        @event.listens_for(self.engine, "connect")
        def foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.addCleanup(self.db.close)
        self.db.execute(text("INSERT INTO offers_raw (id, name) VALUES (1, 'Offer')"))
        self.db.execute(text("INSERT INTO offer_sources (id, offer_id) VALUES (1, 1)"))
        self.db.execute(text("INSERT INTO offer_profiles (id, offer_source_id, name) VALUES (1, 1, 'Profile'), (2, 1, 'Other')"))
        self.db.execute(text("INSERT INTO page_blueprint (id, offer_profile_id, name, description) VALUES (10, 1, 'Structure', ''), (20, 2, 'Other', '')"))
        self.db.execute(text("""INSERT INTO page_blueprint_sections (page_blueprint_id, type, name, purpose, position, is_optional)
            VALUES (10, 'custom', 'Intro', 'Introduce', 1, 0), (10, 'custom', 'Detail', 'Explain', 2, 1)"""))
        self.db.commit()
        blueprint_repo = PageBlueprintRepository(Mock(), self.db)
        sections_repo = PageBlueprintSectionsRepository(Mock(), self.db)
        self.page_repo = PageRepository(Mock(), self.db)
        self.page_service = PageService(self.page_repo)
        self.composer = Mock()
        self.composer.compose.return_value = "FACTUAL OFFER CONTEXT"
        self.ai = Mock()
        self.container = SimpleNamespace(
            db=lambda: self.db,
            llm_context_composer=lambda: self.composer,
            page_blueprint_service=lambda: PageBlueprintService(Mock(), blueprint_repo, PageBlueprintAssembler(Mock(), sections_repo)),
            page_repository=lambda: self.page_repo,
            page_service=lambda: self.page_service,
            offer_profile_service=lambda: SimpleNamespace(get_offer_profile_details_by_id=lambda profile_id: True),
            ai_service=lambda: self.ai,
        )
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(generation, "Container", lambda: self.container))
        stack.enter_context(patch.object(retrieval, "Container", lambda: self.container))

    def output(self, types=("custom", "custom")):
        self.ai.chat_llm.return_value = SimpleNamespace(content=json.dumps({
            "name": "Product page", "description": "Explain the offer", "sections": [
                {"type": kind, "name": f"Section {index}", "content": f"Copy {index}", "position": index}
                for index, kind in enumerate(types, 1)
            ],
        }))

    def test_without_blueprint_uses_offer_and_instructions_and_saves_ordered_sections(self):
        self.output()
        page = generation.generate_page_handler(1, GeneratePageRequest(generation_instructions="Clear language"))
        self.assertEqual(page["offer_profile_id"], 1)
        self.assertIsNone(page["page_blueprint_id"])
        self.assertEqual([section["type"] for section in page["sections"]], ["custom", "custom"])
        self.assertEqual(len(self.page_service.get_by_offer_profile_id(1)), 1)
        self.assertEqual(self.page_service.get_by_offer_profile_id(2), [])
        prompt = json.loads(self.ai.chat_llm.call_args.kwargs["messages"][1].content)
        self.assertEqual(prompt["offer_context"], "FACTUAL OFFER CONTEXT")
        self.assertEqual(prompt["generation_instructions"], "Clear language")
        self.assertNotIn("page_blueprint", prompt)

    def test_selected_blueprint_shapes_output_and_wrong_order_does_not_save(self):
        self.output()
        page = generation.generate_page_handler(1, GeneratePageRequest(page_blueprint_id=10))
        self.assertEqual(page["page_blueprint_id"], 10)
        prompt = json.loads(self.ai.chat_llm.call_args.kwargs["messages"][1].content)
        self.assertEqual([section["type"] for section in prompt["page_blueprint"]["sections"]], ["custom", "custom"])
        self.assertEqual([section["position"] for section in page["sections"]], [1, 2])
        self.output(("custom", "hero"))
        with self.assertRaises(LlmGenerationError):
            generation.generate_page_handler(1, GeneratePageRequest(page_blueprint_id=10))
        self.assertEqual(self.db.query(Page).count(), 1)

    def test_blueprint_must_belong_to_profile_and_generation_is_atomic(self):
        with self.assertRaises(HTTPException) as error:
            generation.generate_page_handler(1, GeneratePageRequest(page_blueprint_id=20))
        self.assertEqual(error.exception.status_code, 422)
        self.ai.chat_llm.assert_not_called()
        self.output(("custom",))
        def fail_after_partial_write(page, sections):
            self.db.add(page)
            self.db.flush()
            sections[0].page_id = page.id
            self.db.add(sections[0])
            self.db.flush()
            raise RuntimeError("section write failed")

        with patch.object(self.page_repo, "create", side_effect=fail_after_partial_write):
            with self.assertRaises(RuntimeError):
                generation.generate_page_handler(1, GeneratePageRequest())
        self.assertEqual(self.db.query(Page).count(), 0)
        self.assertEqual(self.page_repo.get_sections(1), [])

    def test_delete_cascades_sections_but_blueprint_deletion_keeps_page(self):
        self.output()
        page = generation.generate_page_handler(1, GeneratePageRequest(page_blueprint_id=10))
        self.db.execute(text("DELETE FROM page_blueprint WHERE id=10"))
        self.db.commit()
        self.db.expire_all()
        self.assertIsNone(self.page_service.get_by_id(page["id"])["page_blueprint_id"])
        self.assertEqual(len(self.page_service.get_by_id(page["id"])["sections"]), 2)
        self.assertEqual(retrieval.delete_page_handler(page["id"]), {"deleted": True})
        self.assertEqual(self.page_repo.get_sections(page["id"]), [])

    def test_http_contract_and_validation(self):
        with self.assertRaises(ValidationError):
            GeneratePageRequest(page_blueprint_id=0)
        router = APIRouter()
        register_general_routes(router)
        app = FastAPI()
        app.include_router(router)
        self.output(("custom",))
        with TestClient(app) as client:
            self.assertEqual(client.post("/offer-profiles/1/pages/generate", json={"page_blueprint_id": 0}).status_code, 422)
            created = client.post("/offer-profiles/1/pages/generate", json={"generation_instructions": "Simple"})
            self.assertEqual(created.status_code, 200, created.text)
            page_id = created.json()["id"]
            self.assertEqual(client.get(f"/pages/{page_id}").json()["sections"][0]["content"], "Copy 1")
            self.assertEqual(len(client.get("/offer-profiles/1/pages").json()), 1)
            self.assertEqual(client.delete(f"/pages/{page_id}/delete").status_code, 200)
            self.assertEqual(client.get(f"/pages/{page_id}").status_code, 404)

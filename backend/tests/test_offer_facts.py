import json
import xml.etree.ElementTree as ET
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from api.routes.offer_facts_routes import router
import importlib
from contextlib import ExitStack
from application.handlers.offer_facts.generate_offer_facts_handler import SYSTEM_PROMPT
from application.assemblers.offer_source_assembler import OfferSourceAssembler
from application.services.offer_source_service import OfferSourceService
from application.services.offer_facts_service import OfferFactsService
from application.dtos.offer_sources.offer_source_dto import OfferSourceDto
from infrastructure.database.db import Base
from infrastructure.repositories.offer_facts_repository import OfferFactsRepository
from domain.models import models
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource
from domain.models.offer.offer_fact import OfferFact


class OfferFactsTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        @event.listens_for(self.engine, "connect")
        def enable_fks(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add(OfferRaw(id=1, name="Raw product", description="Weight: 99 kg. Raw offer only."))
        self.db.flush()
        self.db.add_all([OfferSource(id=1, offer_id=1, offer_summary="Weight: 2 kg. Includes a USB cable."), OfferSource(id=2, offer_id=1)])
        self.db.commit()
        self.repo = OfferFactsRepository(None, self.db)
        self.ai = SimpleNamespace(content=json.dumps({"offer_facts": []}))
        self.calls = []
        def chat(messages, **kwargs):
            self.calls.append((messages, kwargs))
            return self.ai
        self.container = SimpleNamespace(
            offer_source_repository=lambda: SimpleNamespace(get_by_id=lambda id: self.db.get(OfferSource, id)),
            offers_repository=lambda: SimpleNamespace(get_by_id=lambda id: self.db.get(OfferRaw, id)),
            offer_facts_repository=lambda: self.repo,
            ai_service=lambda: SimpleNamespace(chat_llm=chat),
        )
        source_service = OfferSourceService(None, None, None, None, None, self.container.offer_source_repository(), None)
        self.container.offer_source_service = lambda: source_service
        self.container.offer_facts_service = lambda: OfferFactsService(self.repo)
        self.override = ExitStack()
        for name in ('list_offer_facts_handler', 'create_offer_fact_handler', 'update_offer_fact_handler', 'delete_offer_fact_handler', 'generate_offer_facts_handler'):
            module = importlib.import_module(f"application.handlers.offer_facts.{name}")
            self.override.enter_context(patch.object(module, "Container", lambda: self.container))
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)
        self.fields = {"name": "Weight", "description": "The product weighs 2 kg.", "evidence": "Weight: 2 kg."}

    def tearDown(self):
        self.client.close()
        self.override.close()
        self.db.close()
        self.engine.dispose()

    def create(self):
        response = self.client.post("/offer-sources/1/facts", json=self.fields)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_extraction_evidence_duplicates_and_repeat_generation(self):
        self.ai.content = json.dumps({"offer_facts": [self.fields, self.fields, {**self.fields, "name": "Invented", "description": "Invented claim", "evidence": "Lifetime warranty"}]})
        first = self.client.post("/offer-sources/1/facts/generate")
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(first.json()["created_count"], 1)
        self.assertEqual(first.json()["skipped_count"], 2)
        self.assertFalse(first.json()["items"][0]["is_reviewed"])
        second = self.client.post("/offer-sources/1/facts/generate")
        self.assertEqual(second.json()["created_count"], 0)
        self.assertTrue(self.calls[0][1]["json_response"])
        user_context = self.calls[0][0][1].content
        section = user_context[user_context.index('<offer_source '):user_context.index('</offer_source>') + len('</offer_source>')]
        source_context = ET.fromstring(section)
        self.assertEqual(json.loads(source_context.text), {"offer_summary": "Weight: 2 kg. Includes a USB cable."})
        self.assertTrue(source_context.attrib["purpose"])
        self.assertIn('<offer_facts purpose=', user_context)
        self.assertNotIn("original_offer", user_context)
        self.assertNotIn("99 kg", user_context)
        self.assertEqual(self.db.query(OfferFact).count(), 1)

    def test_uses_only_offer_source_for_generation_and_quotes(self):
        def raw_access():
            raise AssertionError("Raw offer must not be accessed")
        self.container.offers_repository = raw_access
        self.ai.content = json.dumps({"offer_facts": [self.fields]})
        generated = self.client.post("/offer-sources/1/facts/generate")
        self.assertEqual(generated.status_code, 200, generated.text)
        self.assertEqual(generated.json()["created_count"], 1)
        invalid = self.client.post("/offer-sources/1/facts", json={**self.fields, "evidence": "Weight: 99 kg."})
        self.assertEqual(invalid.status_code, 422)
        self.assertIn("do not translate", SYSTEM_PROMPT)
        empty = self.client.post("/offer-sources/2/facts/generate")
        self.assertEqual(empty.status_code, 200, empty.text)
        self.assertEqual(empty.json()["created_count"], 0)
        self.assertEqual(len(self.calls), 1)

    def test_context_services_keep_source_separate_and_filter_facts(self):
        self.create()
        self.repo.create_many([OfferFact(offer_source_id=1, name="Cable", description="Includes USB cable.", evidence=None, is_reviewed=True)])
        facts_service = self.container.offer_facts_service()
        reviewed = ET.fromstring(facts_service.build_llm_context(1))
        self.assertEqual([fact["name"] for fact in json.loads(reviewed.text)], ["Cable"])
        all_facts = ET.fromstring(facts_service.build_llm_context(1, include_unreviewed=True))
        content = json.loads(all_facts.text)
        self.assertEqual(len(content), 2)
        self.assertNotIn("id", content[0])
        self.assertIn("duplicate detection only", all_facts.attrib["purpose"])
        source = ET.fromstring(self.container.offer_source_service().build_llm_context(1, include_related=False))
        self.assertEqual(set(json.loads(source.text)), {"offer_summary"})
        self.assertNotIn("offer_facts", source.text)
        self.assertNotIn("99 kg", source.text)

    def test_invalid_model_output_is_atomic(self):
        for payload in ("bad json", json.dumps({"offer_facts": [self.fields, {"name": "Broken"}]}), json.dumps({"offer_facts": [self.fields, None]})):
            self.ai.content = payload
            response = self.client.post("/offer-sources/1/facts/generate")
            self.assertEqual(response.status_code, 502)
            self.assertEqual(self.db.query(OfferFact).count(), 0)

    def test_crud_review_and_pagination(self):
        fact = self.create()
        id = fact["id"]
        checked = self.client.post(f"/offer-facts/{id}/update", json={"fields": {"is_reviewed": True}})
        self.assertTrue(checked.json()["is_reviewed"])
        changed = self.client.post(f"/offer-facts/{id}/update", json={"fields": {"description": "Weight is 2 kg."}})
        self.assertFalse(changed.json()["is_reviewed"])
        listing = self.client.get("/offer-sources/1/facts", params={"search": "USB", "page_size": 1})
        self.assertEqual(listing.json()["total_items"], 0)
        listing = self.client.get("/offer-sources/1/facts", params={"search": "2 kg", "is_reviewed": "false", "page_size": 1})
        self.assertEqual(listing.json()["total_items"], 1)
        self.assertEqual(self.client.get("/offer-sources/2/facts").json()["total_items"], 0)
        self.assertEqual(self.client.delete(f"/offer-facts/{id}/delete").status_code, 200)
        self.assertEqual(self.client.delete(f"/offer-facts/{id}/delete").status_code, 404)

    def test_update_accepts_old_or_manually_edited_evidence(self):
        fact = self.create()
        id = fact["id"]
        source = self.db.get(OfferSource, 1)
        source.offer_summary = "Updated source without the old quote."
        self.db.commit()
        checked = self.client.post(f"/offer-facts/{id}/update", json={"fields": {"is_reviewed": True}})
        self.assertEqual(checked.status_code, 200, checked.text)
        self.assertTrue(checked.json()["is_reviewed"])
        edited = self.client.post(f"/offer-facts/{id}/update", json={"fields": {"description": "Manually corrected fact.", "evidence": "Manually corrected reference."}})
        self.assertEqual(edited.status_code, 200, edited.text)
        self.assertEqual(edited.json()["evidence"], "Manually corrected reference.")
        self.assertEqual(self.repo.get_by_id(id).evidence, "Manually corrected reference.")
        self.assertFalse(edited.json()["is_reviewed"])
        cleared = self.client.post(f"/offer-facts/{id}/update", json={"fields": {"evidence": None}})
        self.assertEqual(cleared.status_code, 200, cleared.text)
        self.assertIsNone(cleared.json()["evidence"])

    def test_evidence_is_returned_for_ui_but_excluded_from_contexts(self):
        fact = self.create()
        self.assertEqual(fact["evidence"], "Weight: 2 kg.")
        self.assertEqual(self.repo.get_by_id(fact["id"]).evidence, "Weight: 2 kg.")
        listing = self.client.get("/offer-sources/1/facts").json()
        self.assertEqual(listing["items"][0]["evidence"], "Weight: 2 kg.")
        changed = self.client.post(f"/offer-facts/{fact['id']}/update", json={"fields": {"name": "Updated weight"}})
        self.assertEqual(changed.json()["evidence"], "Weight: 2 kg.")
        self.assertEqual(self.repo.get_by_id(fact["id"]).evidence, "Weight: 2 kg.")
        context = self.container.offer_facts_service().build_llm_context(1, include_unreviewed=True)
        self.assertNotIn('"evidence"', context)

    def test_validation_and_missing_source(self):
        for fields in ({**self.fields, "name": " "}, {**self.fields, "evidence": "not in source"}, {**self.fields, "source_field": "description"}):
            self.assertEqual(self.client.post("/offer-sources/1/facts", json=fields).status_code, 422)
        for path in ("/offer-sources/999/facts",):
            self.assertEqual(self.client.get(path).status_code, 404)
        self.assertEqual(self.client.post("/offer-sources/999/facts/generate").status_code, 404)
        fact = self.create()
        self.assertEqual(self.client.post(f"/offer-facts/{fact['id']}/update", json={"fields": {"offer_source_id": 2}}).status_code, 422)

    def test_evidence_is_optional_for_creation_update_and_generation(self):
        for evidence in (None, "", "   "):
            response = self.client.post("/offer-sources/1/facts", json={**self.fields, "evidence": evidence})
            self.assertEqual(response.status_code, 201, response.text)
            self.assertNotIn("source_field", response.json())
        fields = {key: value for key, value in self.fields.items() if key != "evidence"}
        response = self.client.post("/offer-sources/1/facts", json=fields)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertIsNone(response.json()["evidence"])
        id = self.create()["id"]
        cleared = self.client.post(f"/offer-facts/{id}/update", json={"fields": {"evidence": None}})
        self.assertEqual(cleared.status_code, 200, cleared.text)
        self.assertIsNone(cleared.json()["evidence"])
        self.ai.content = json.dumps({"offer_facts": [{"name": "Cable", "description": "A USB cable is included."}]})
        generated = self.client.post("/offer-sources/1/facts/generate")
        self.assertEqual(generated.status_code, 200, generated.text)
        self.assertEqual(generated.json()["created_count"], 1)
        self.assertIsNone(generated.json()["items"][0]["evidence"])

    def test_legacy_migration_preserves_rows_and_allows_missing_evidence(self):
        from infrastructure.database import init_db as migration
        from sqlalchemy import inspect
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE offer_facts"))
            conn.execute(text("""CREATE TABLE offer_facts (
                id INTEGER PRIMARY KEY, offer_source_id INTEGER NOT NULL REFERENCES offer_sources(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL, description TEXT NOT NULL, evidence TEXT NOT NULL,
                source_field VARCHAR(32) NOT NULL, is_reviewed BOOLEAN NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""))
            conn.execute(text("""INSERT INTO offer_facts (id, offer_source_id, name, description, evidence, source_field, is_reviewed)
                VALUES (1, 1, 'Weight', 'The product weighs 2 kg.', 'Weight: 2 kg.', 'description', 1)"""))
            before = tuple(conn.execute(text("SELECT id, offer_source_id, name, description, evidence, is_reviewed, created_at, updated_at FROM offer_facts")).one())
        with patch.object(migration, "engine", self.engine):
            migration._migrate_offer_facts_optional_evidence()
            migration._migrate_offer_facts_optional_evidence()
        inspector = inspect(self.engine)
        columns = {column["name"]: column for column in inspector.get_columns("offer_facts")}
        self.assertNotIn("source_field", columns)
        self.assertTrue(columns["evidence"]["nullable"])
        self.assertEqual(len(inspector.get_indexes("offer_facts")), 2)
        with self.engine.connect() as conn:
            after = tuple(conn.execute(text("SELECT id, offer_source_id, name, description, evidence, is_reviewed, created_at, updated_at FROM offer_facts")).one())
            self.assertEqual(before, after)
            self.assertFalse(conn.execute(text("PRAGMA foreign_key_check")).fetchall())
        response = self.client.post("/offer-sources/1/facts", json={"name": "Cable", "description": "Includes a USB cable."})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertIsNone(response.json()["evidence"])

    def test_cascade_delete(self):
        self.create()
        self.db.execute(text("DELETE FROM offer_sources WHERE id=1"))
        self.db.commit()
        self.assertEqual(self.db.query(OfferFact).count(), 0)

    def test_only_reviewed_facts_enter_llm_context(self):
        self.create()
        self.repo.create_many([OfferFact(offer_source_id=1, **{**self.fields, "name": "Cable", "description": "A USB cable is included.", "evidence": "Includes a USB cable.", "is_reviewed": True})])
        assembler = OfferSourceAssembler(None, None, self.repo, SimpleNamespace(find_for_offer_source=lambda **kwargs: []))
        dto = assembler.assemble_dto(OfferSourceDto(1, 1, "Summary"))
        self.assertEqual(len(dto.to_dict()["offer_facts"]), 2)
        service = OfferSourceService(None, None, None, None, None, None, None)
        service.get_offer_source_details_by_id = lambda **kwargs: dto
        dto.offer_source_elements = [SimpleNamespace(name="Element to exclude", is_reviewed=True)]
        dto.brand_marketing = {"name": "Brand to exclude"}
        context = service.build_llm_context(1)
        content = json.loads(ET.fromstring(context).text)
        self.assertEqual(set(content), {"offer_summary", "offer_facts"})
        self.assertNotIn("Element to exclude", context)
        self.assertNotIn("Brand to exclude", context)
        self.assertEqual(len(dto.offer_facts), 2)
        self.assertIn("A USB cable is included.", context)
        self.assertNotIn("The product weighs 2 kg.", context)
        self.assertNotIn('"is_reviewed"', context)
        self.assertNotIn('"evidence"', context)


if __name__ == "__main__":
    unittest.main()

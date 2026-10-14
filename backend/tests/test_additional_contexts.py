import importlib
import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from api.routes.additional_contexts_routes import router
from infrastructure.database.db import Base
from infrastructure.repositories.additional_contexts_repository import AdditionalContextsRepository
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository
from domain.models import models
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource
from domain.models.offer.offer_profile import OfferProfile
from domain.models.context.additional_context import AdditionalContext
from domain.models.offer.offer_profile_additional_context import OfferProfileAdditionalContext


class AdditionalContextTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        @event.listens_for(self.engine, "connect")
        def enable_fk(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add(OfferRaw(id=1, name="Product")); self.db.flush()
        self.db.add(OfferSource(id=1, offer_id=1)); self.db.flush()
        self.db.add_all([OfferProfile(id=1, offer_source_id=1, name="A"), OfferProfile(id=2, offer_source_id=1, name="B")]); self.db.commit()
        self.repo = AdditionalContextsRepository(None, self.db)
        profiles = OfferProfilesRepository(None, self.db)
        container = SimpleNamespace(additional_contexts_repository=lambda: self.repo, offer_profiles_repository=lambda: profiles)
        self.overrides = ExitStack()
        for action in ("list", "create", "update", "attach", "detach"):
            plural = "s" if action == "list" else ""
            module = importlib.import_module(f"application.handlers.additional_contexts.{action}_additional_context{plural}_handler")
            self.overrides.enter_context(patch.object(module, "Container", lambda: container))
        app = FastAPI(); app.include_router(router); self.client = TestClient(app)

    def tearDown(self):
        self.client.close(); self.overrides.close(); self.db.close(); self.engine.dispose()

    def create(self):
        response = self.client.post("/offer-profiles/1/additional-contexts", json={"name": "  Context  ", "content": "  Useful content  "})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["name"], "Context")
        self.assertEqual(response.json()["content"], "Useful content")
        return response.json()["id"]

    def test_shared_context_edit_and_detach(self):
        id = self.create()
        self.assertEqual(self.client.get("/offer-profiles/2/additional-contexts").json(), [])
        for _ in range(2):
            self.assertEqual(self.client.post(f"/offer-profiles/2/additional-contexts/{id}").status_code, 200)
        self.assertEqual(self.db.query(OfferProfileAdditionalContext).count(), 2)
        updated = self.client.post(f"/additional-contexts/{id}/update", json={"name": "Updated", "content": "Shared text"})
        self.assertEqual(updated.status_code, 200, updated.text)
        for profile_id in (1, 2):
            self.assertEqual(self.client.get(f"/offer-profiles/{profile_id}/additional-contexts").json()[0]["content"], "Shared text")
        self.assertEqual(self.client.delete(f"/offer-profiles/1/additional-contexts/{id}").status_code, 200)
        self.assertEqual(self.client.get("/offer-profiles/1/additional-contexts").json(), [])
        self.assertEqual(len(self.client.get("/offer-profiles/2/additional-contexts").json()), 1)
        self.assertEqual(len(self.client.get("/additional-contexts").json()), 1)

    def test_cascade_deletes_links_without_deleting_context(self):
        id = self.create()
        self.db.execute(text("DELETE FROM offer_profiles WHERE id=1")); self.db.commit()
        self.assertEqual(self.db.query(OfferProfileAdditionalContext).count(), 0)
        self.assertIsNotNone(self.repo.get_by_id(id))
        self.client.post(f"/offer-profiles/2/additional-contexts/{id}")
        self.db.delete(self.repo.get_by_id(id)); self.db.commit()
        self.assertEqual(self.db.query(OfferProfileAdditionalContext).count(), 0)

    def test_startup_preserves_profile_link_and_repairs_old_bad_column(self):
        from infrastructure.database import init_db as migration
        from sqlalchemy import inspect
        id = self.create()
        with patch.object(migration, "engine", self.engine):
            migration.init_db(); migration.init_db()
            columns = {column["name"] for column in inspect(self.engine).get_columns("offer_profile_additional_contexts")}
            self.assertIn("offer_profile_id", columns)
            self.assertNotIn("offer_source_id", columns)
            with self.engine.begin() as conn:
                conn.execute(text('ALTER TABLE offer_profile_additional_contexts RENAME COLUMN offer_profile_id TO offer_source_id'))
            migration.init_db(); migration.init_db()
        result = self.client.get("/offer-profiles/1/additional-contexts")
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()[0]["id"], id)
        self.assertEqual(self.db.query(OfferProfileAdditionalContext).count(), 1)
        with self.engine.connect() as conn:
            self.assertFalse(conn.execute(text('PRAGMA foreign_key_check')).fetchall())

    def test_validation_missing_entities_and_no_partial_creation(self):
        for payload in ({"name": " ", "content": "text"}, {"name": "name", "content": " "}, {"name": "x" * 256, "content": "text"}):
            self.assertEqual(self.client.post("/offer-profiles/1/additional-contexts", json=payload).status_code, 422)
        self.assertEqual(self.client.post("/offer-profiles/999/additional-contexts", json={"name": "name", "content": "text"}).status_code, 404)
        self.assertEqual(self.db.query(AdditionalContext).count(), 0)
        self.assertEqual(self.client.get("/offer-profiles/999/additional-contexts").status_code, 404)
        self.assertEqual(self.client.post("/offer-profiles/1/additional-contexts/999").status_code, 404)
        self.assertEqual(self.client.delete("/offer-profiles/1/additional-contexts/999").status_code, 404)
        self.assertEqual(self.client.post("/additional-contexts/999/update", json={"name": "name", "content": "text"}).status_code, 404)


if __name__ == "__main__":
    unittest.main()

import unittest
import importlib
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from api.routes.offer_profiles_routes import router
from application.handlers.offer_profiles import create_offer_profile_handler, list_offer_profiles_handler
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository
from infrastructure.repositories.additional_contexts_repository import AdditionalContextsRepository
from application.services.offer_profile_service import OfferProfileService
from application.assemblers.offer_profile_assembler import OfferProfileAssembler
from infrastructure.database.db import Base
from infrastructure.database import init_db as migration
from domain.models import models
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource


class OfferProfileTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        @event.listens_for(self.engine, "connect")
        def enable_fk(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add(OfferRaw(id=1, name="Product")); self.db.flush()
        self.db.add_all([OfferSource(id=1, offer_id=1), OfferSource(id=2, offer_id=1)]); self.db.commit()
        repo = OfferProfilesRepository(None, self.db)
        container = SimpleNamespace(offer_profiles_repository=lambda: repo, offer_source_repository=lambda: SimpleNamespace(get_by_id=lambda id: self.db.get(OfferSource, id)))
        service = OfferProfileService(repo, OfferProfileAssembler(AdditionalContextsRepository(None, self.db)))
        container.offer_profile_service = lambda: service
        self.overrides = ExitStack()
        for action in ("create", "list", "get", "update", "delete"):
            module = importlib.import_module(f"application.handlers.offer_profiles.{action}_offer_profile{'s' if action == 'list' else ''}_handler")
            self.overrides.enter_context(patch.object(module, "Container", lambda: container))
        app = FastAPI(); app.include_router(router); self.client = TestClient(app)

    def tearDown(self):
        self.client.close(); self.overrides.close(); self.db.close(); self.engine.dispose()

    def test_create_and_source_scoped_list(self):
        response = self.client.post("/offer-sources/1/profiles", json={"name": "  Retail  "})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["name"], "Retail")
        self.assertEqual(response.json()["offer_source_id"], 1)
        self.assertEqual(len(self.client.get("/offer-sources/1/profiles").json()), 1)
        self.assertEqual(self.client.get("/offer-sources/2/profiles").json(), [])

    def test_name_validation_and_missing_source(self):
        for name in ("", "   ", "x" * 256):
            self.assertEqual(self.client.post("/offer-sources/1/profiles", json={"name": name}).status_code, 422)
        self.assertEqual(self.client.post("/offer-sources/999/profiles", json={"name": "Profile"}).status_code, 404)
        self.assertEqual(self.client.get("/offer-sources/999/profiles").status_code, 404)

    def test_profile_detail_edit_delete_and_missing_id(self):
        created = self.client.post("/offer-sources/1/profiles", json={"name": "Original"}).json()
        id = created["id"]
        detail = self.client.get(f"/offer-profiles/{id}")
        self.assertEqual(detail.status_code, 200, detail.text)
        self.assertEqual(detail.json()["name"], "Original")
        for name in ("", "   ", "x" * 256):
            self.assertEqual(self.client.post(f"/offer-profiles/{id}/update", json={"name": name}).status_code, 422)
        self.assertEqual(self.client.post(f"/offer-profiles/{id}/update", json={"name": "Other", "offer_source_id": 2}).status_code, 422)
        updated = self.client.post(f"/offer-profiles/{id}/update", json={"name": "  Updated  "})
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertEqual(updated.json()["name"], "Updated")
        self.assertEqual(updated.json()["offer_source_id"], 1)
        self.assertEqual(self.client.get("/offer-sources/1/profiles").json()[0]["name"], "Updated")
        self.assertEqual(self.client.delete(f"/offer-profiles/{id}/delete").status_code, 200)
        self.assertEqual(self.client.get("/offer-sources/1/profiles").json(), [])
        self.assertEqual(self.client.get(f"/offer-profiles/{id}").status_code, 404)
        self.assertEqual(self.client.post(f"/offer-profiles/{id}/update", json={"name": "Missing"}).status_code, 404)
        self.assertEqual(self.client.delete(f"/offer-profiles/{id}/delete").status_code, 404)

    def test_repeated_startup_preserves_new_profiles(self):
        self.client.post("/offer-sources/1/profiles", json={"name": "Keep me"})
        with patch.object(migration, "engine", self.engine):
            migration.init_db(); migration.init_db()
        self.assertIn("offer_profiles", inspect(self.engine).get_table_names())
        profiles = self.client.get("/offer-sources/1/profiles").json()
        self.assertEqual(profiles[0]["name"], "Keep me")
        self.assertEqual(inspect(self.engine).get_foreign_keys("offer_profiles")[0]["referred_table"], "offer_sources")


if __name__ == "__main__":
    unittest.main()

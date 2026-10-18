import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from api.routes.notes_routes import router
from api.__routes__ import Routes
from application.assemblers.offer_profile_assembler import OfferProfileAssembler
from application.services.offer_profile_service import OfferProfileService
from domain.models import models
from domain.models.context.note import Note
from domain.models.offer.offer_profile_note import OfferProfileNote
from domain.models.offer.offer_profile import OfferProfile
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource
from infrastructure.database.db import Base
from infrastructure.repositories.additional_contexts_repository import AdditionalContextsRepository
from infrastructure.repositories.notes_repository import NotesRepository
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository


class NotesTests(unittest.TestCase):
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
        self.repo = NotesRepository(None, self.db)
        self.profiles = OfferProfilesRepository(None, self.db)
        container = SimpleNamespace(notes_repository=lambda: self.repo, offer_profiles_repository=lambda: self.profiles)
        self.patcher = patch("application.handlers.notes.notes_handlers.Container", lambda: container)
        self.patcher.start()
        app = FastAPI(); app.include_router(router); self.client = TestClient(app)

    def tearDown(self):
        self.client.close(); self.patcher.stop(); self.db.close(); self.engine.dispose()

    def create(self):
        response = self.client.post("/offer-profiles/1/notes", json={"title": "  Brief  ", "content": "  Internal note  "})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["title"], "Brief")
        self.assertEqual(response.json()["content"], "Internal note")
        return response.json()["id"]

    def test_shared_edit_detach_and_delete(self):
        note_id = self.create()
        for _ in range(2):
            self.assertEqual(self.client.post(f"/offer-profiles/2/notes/{note_id}").status_code, 200)
        self.assertEqual(self.db.query(OfferProfileNote).count(), 2)
        updated = self.client.post(f"/notes/{note_id}/update", json={"title": "Updated", "content": "Shared text"})
        self.assertEqual(updated.status_code, 200, updated.text)
        for profile_id in (1, 2):
            self.assertEqual(self.client.get(f"/offer-profiles/{profile_id}/notes").json()[0]["content"], "Shared text")
        self.assertEqual(self.client.delete(f"/offer-profiles/1/notes/{note_id}").status_code, 200)
        self.assertEqual(self.client.get("/offer-profiles/1/notes").json(), [])
        self.assertEqual(len(self.client.get("/offer-profiles/2/notes").json()), 1)
        self.assertEqual(len(self.client.get("/notes").json()), 1)
        self.assertEqual(self.client.delete(f"/notes/{note_id}").status_code, 200)
        self.assertEqual(self.db.query(OfferProfileNote).count(), 0)
        self.assertEqual(self.db.query(Note).count(), 0)

    def test_standalone_note_is_listed_and_can_be_attached_later(self):
        response = self.client.post("/notes", json={"title": "Loose note", "content": "Save for later"})
        self.assertEqual(response.status_code, 201, response.text)
        note_id = response.json()["id"]
        self.assertEqual(self.db.query(OfferProfileNote).count(), 0)
        self.assertEqual(self.client.get("/notes").json()[0]["id"], note_id)
        self.assertEqual(self.client.get("/offer-profiles/1/notes").json(), [])
        self.assertEqual(self.client.post(f"/offer-profiles/1/notes/{note_id}").status_code, 200)
        self.assertEqual(self.client.get("/offer-profiles/1/notes").json()[0]["id"], note_id)

    def test_standalone_create_works_through_application_router(self):
        app = FastAPI()
        routes = Routes(app)
        routes.register()
        with TestClient(app) as client:
            response = client.post("/notes", json={"title": "Global", "content": "Without profile"})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(self.db.query(OfferProfileNote).count(), 0)

    def test_notes_do_not_enter_offer_profile_llm_context(self):
        self.create()
        service = OfferProfileService(self.profiles, OfferProfileAssembler(AdditionalContextsRepository(None, self.db)))
        self.assertNotIn("Internal note", service.build_llm_context(1))
        self.assertNotIn("notes", service.build_llm_context(1))

    def test_cascade_and_validation(self):
        note_id = self.create()
        self.db.execute(text("DELETE FROM offer_profiles WHERE id=1")); self.db.commit()
        self.assertEqual(self.db.query(OfferProfileNote).count(), 0)
        self.assertIsNotNone(self.repo.get_by_id(note_id))
        self.assertEqual(self.client.post(f"/offer-profiles/2/notes/{note_id}").status_code, 200)
        self.assertEqual(self.client.post("/offer-profiles/999/notes", json={"title": "X", "content": "Y"}).status_code, 404)
        self.assertEqual(self.client.get("/offer-profiles/999/notes").status_code, 404)
        self.assertEqual(self.client.post("/offer-profiles/2/notes/999").status_code, 404)
        self.assertEqual(self.client.delete("/offer-profiles/2/notes/999").status_code, 404)
        self.assertEqual(self.client.delete("/notes/999").status_code, 404)
        for payload in ({"title": " ", "content": "Text"}, {"title": "Title", "content": " "}, {"title": "x" * 256, "content": "Text"}):
            self.assertEqual(self.client.post("/offer-profiles/2/notes", json=payload).status_code, 422)
        self.assertEqual(self.db.query(Note).count(), 1)


if __name__ == "__main__":
    unittest.main()

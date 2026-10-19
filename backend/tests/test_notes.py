import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from api.routes.notes_routes import router
from api.__routes__ import Routes
from domain.models import models
from domain.models.context.note import Note
from infrastructure.database.db import Base
from infrastructure.repositories.notes_repository import NotesRepository


class NotesTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.repo = NotesRepository(None, self.db)
        container = SimpleNamespace(notes_repository=lambda: self.repo)
        self.patcher = patch("application.handlers.notes.notes_handlers.Container", lambda: container)
        self.patcher.start()
        app = FastAPI(); app.include_router(router); self.client = TestClient(app)

    def tearDown(self):
        self.client.close(); self.patcher.stop(); self.db.close(); self.engine.dispose()

    def create(self):
        response = self.client.post("/notes", json={"title": "  Brief  ", "content": "  Internal note  "})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["title"], "Brief")
        self.assertEqual(response.json()["content"], "Internal note")
        return response.json()["id"]

    def test_create_list_update_and_delete(self):
        note_id = self.create()
        self.assertEqual(self.client.get("/notes").json()[0]["id"], note_id)
        updated = self.client.post(f"/notes/{note_id}/update", json={"title": "Updated", "content": "New text"})
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertEqual(self.client.get("/notes").json()[0]["content"], "New text")
        self.assertEqual(self.client.delete(f"/notes/{note_id}").status_code, 200)
        self.assertEqual(self.db.query(Note).count(), 0)

    def test_create_works_through_application_router(self):
        app = FastAPI()
        Routes(app).register()
        with TestClient(app) as client:
            response = client.post("/notes", json={"title": "Global", "content": "Text"})
        self.assertEqual(response.status_code, 201, response.text)

    def test_notes_are_not_linked_to_offer_profiles(self):
        self.assertNotIn("offer_profile_notes", inspect(self.engine).get_table_names())
        self.assertEqual(self.client.get("/offer-profiles/1/notes").status_code, 404)

    def test_validation_and_missing_notes(self):
        self.assertEqual(self.client.post("/notes/999/update", json={"title": "X", "content": "Y"}).status_code, 404)
        self.assertEqual(self.client.delete("/notes/999").status_code, 404)
        for payload in ({"title": " ", "content": "Text"}, {"title": "Title", "content": " "}, {"title": "x" * 256, "content": "Text"}):
            self.assertEqual(self.client.post("/notes", json=payload).status_code, 422)
        self.assertEqual(self.db.query(Note).count(), 0)


if __name__ == "__main__":
    unittest.main()

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
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

    def test_pin_unpin_and_order(self):
        first_id = self.create()
        second = self.client.post("/notes", json={"title": "Zebra", "content": "Text"}).json()
        response = self.client.post(f"/notes/{second['id']}/pin", json={"is_pinned": True})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["is_pinned"])
        self.assertEqual([note["id"] for note in self.client.get("/notes").json()], [second["id"], first_id])
        updated = self.client.post(f"/notes/{second['id']}/update", json={"title": "Renamed", "content": "New text"})
        self.assertTrue(updated.json()["is_pinned"])
        response = self.client.post(f"/notes/{second['id']}/pin", json={"is_pinned": False})
        self.assertFalse(response.json()["is_pinned"])
        self.assertEqual(self.client.get("/notes").json()[0]["id"], first_id)

    def test_pin_migration_preserves_legacy_notes(self):
        from infrastructure.database import init_db as migration

        legacy = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        try:
            with legacy.begin() as conn:
                conn.execute(text("CREATE TABLE notes (id INTEGER PRIMARY KEY, title VARCHAR(255) NOT NULL, content TEXT NOT NULL)"))
                conn.execute(text("INSERT INTO notes (id, title, content) VALUES (1, 'Old', 'Kept')"))
            with patch.object(migration, "engine", legacy):
                migration._add_note_pinned_column()
                migration._add_note_pinned_column()
            with legacy.connect() as conn:
                row = conn.execute(text("SELECT title, content, is_pinned FROM notes WHERE id = 1")).one()
            self.assertEqual(tuple(row), ("Old", "Kept", 0))
        finally:
            legacy.dispose()

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
        self.assertEqual(self.client.post("/notes/999/pin", json={"is_pinned": True}).status_code, 404)
        self.assertEqual(self.client.post("/notes/1/pin", json={"is_pinned": "maybe"}).status_code, 422)
        self.assertEqual(self.client.delete("/notes/999").status_code, 404)
        for payload in ({"title": " ", "content": "Text"}, {"title": "Title", "content": " "}, {"title": "x" * 256, "content": "Text"}):
            self.assertEqual(self.client.post("/notes", json=payload).status_code, 422)
        self.assertEqual(self.db.query(Note).count(), 0)


if __name__ == "__main__":
    unittest.main()

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session

from api.routes import ad_copy_routes as routes
from application.dtos.ad_copy.ad_copy_fields import AdCopyFields, GenerateAdCopyRequest, UpdateAdCopyRequest
from application.handlers.ad_copy import ad_copy_handlers as handlers
from application.handlers.ad_copy import generate_ad_copy_handler as generation
from application.services.llm_context_composer import ContextRef, ContextSelection
from domain.enums.context_type import ContextType
from domain.models import models
from domain.models.ad.ad_copy import AdCopy
from infrastructure.database.db import Base
from infrastructure.database import init_db as migrations
from infrastructure.repositories.ad_copies_repository import AdCopiesRepository
from infrastructure.repositories.ad_copy_structures_repository import AdCopyStructuresRepository
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository
from infrastructure.services.path_service import PathService


class AdCopyTests(unittest.TestCase):
    FIELDS = {"name": "Convenience", "primary_text": "Discover a simpler way to use the service.",
              "headline": "A simpler routine", "description": "Learn how the service works."}

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        @event.listens_for(self.engine, "connect")
        def foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO offers_raw (id, name) VALUES (1, 'Service')"))
            conn.execute(text("INSERT INTO offer_sources (id, offer_id, offer_details) VALUES (1, 1, 'Source')"))
            conn.execute(text("INSERT INTO offer_profiles (id, offer_source_id, name) VALUES (1, 1, 'Profile'), (2, 1, 'Other')"))
        self.db = Session(self.engine)
        self.repo = AdCopiesRepository(None, self.db)
        self.structures = AdCopyStructuresRepository(PathService(None))
        self.composer = Mock()
        self.composer.compose.return_value = "<offer_profile>Profile</offer_profile><offer_source>Source</offer_source>"
        self.ai = Mock()
        self.ai.chat_json.return_value = {"copies": [self.FIELDS.copy()]}
        container = SimpleNamespace(
            llm_context_composer=lambda: self.composer, ai_service=lambda: self.ai,
            ad_copies_repository=lambda: self.repo,
            ad_copy_structures_repository=lambda: self.structures,
            offer_profiles_repository=lambda: OfferProfilesRepository(None, self.db),
        )
        for module in (handlers, generation):
            patcher = patch.object(module, "Container", lambda: container)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.engine.dispose)
        self.addCleanup(self.db.close)

    def test_generation_uses_composer_with_only_profile_and_source(self):
        result = routes.generate_ad_copies(1, GenerateAdCopyRequest(count=1, generation_instructions="Without CTA"))
        self.composer.compose.assert_called_once_with(
            root=ContextRef(ContextType.OFFER_PROFILE, 1), include=[ContextSelection(ContextType.OFFER_SOURCE)],
        )
        self.assertEqual(result[0]["offer_profile_id"], 1)
        self.assertEqual(result[0]["primary_text"], self.FIELDS["primary_text"])
        self.assertFalse(result[0]["is_reviewed"])
        self.assertIsNone(result[0]["cta"])
        call = self.ai.chat_json.call_args.kwargs
        self.assertIn("Without CTA", call["messages"][1].content)
        self.assertIn("<offer_profile>", call["messages"][1].content)
        self.assertIn("<offer_source>", call["messages"][1].content)
        self.assertIsNone(GenerateAdCopyRequest().structure_id)
        self.assertNotIn("selected_ad_copy_structure", call["messages"][1].content)
        self.assertIn("derive the primary_text structure", call["messages"][0].content)
        self.assertIn("exactly one empty line (two newline", call["messages"][0].content)
        self.assertIn("Use 2 to 5 visible emojis in every primary_text", call["messages"][0].content)
        self.assertIn("Keep list items free of emojis", call["messages"][0].content)
        self.assertIn('start every item with "- "', call["messages"][0].content)
        self.assertIn("An offer may concern a product, service, package", call["messages"][0].content)
        self.assertEqual(call["rule_sets"], ())
        self.assertEqual(GenerateAdCopyRequest().count, 3)
        self.assertNotIn("generation_mode", GenerateAdCopyRequest.model_fields)
        self.assertEqual(routes.list_ad_copies(2), [])

    def test_structure_catalog_and_unknown_structure(self):
        catalog = self.structures.get_all()
        self.assertEqual([item["id"] for item in catalog], [f"S{number:02}" for number in range(1, 16)])
        self.assertEqual([step["name"] for step in catalog[0]["structure"]], [
            "Problem hook", "Solution", "Offer details and benefits", "Offer", "Trust or CTA",
        ])
        self.assertEqual([step["name"] for step in catalog[1]["structure"]], [
            "Result", "Offer and mechanism", "Main benefits", "Convenience", "CTA",
        ])
        self.assertEqual([step["name"] for step in catalog[2]["structure"]], [
            "Hook", "Benefits", "Positive result", "Offer or CTA",
        ])
        self.assertIn("line starting with '- '", catalog[2]["rules"][0])
        with patch.object(routes, "Container", lambda: SimpleNamespace(ad_copy_structures_repository=lambda: self.structures)):
            self.assertEqual(routes.list_ad_copy_structures(), catalog)
        routes.generate_ad_copies(1, GenerateAdCopyRequest(count=1, structure_id="S01"))
        prompt = self.ai.chat_json.call_args.kwargs["messages"][1].content
        self.assertIn('"id": "S01"', prompt)
        self.assertIn('"name": "Offer details and benefits"', prompt)
        routes.generate_ad_copies(1, GenerateAdCopyRequest(count=1, structure_id="S02"))
        prompt = self.ai.chat_json.call_args.kwargs["messages"][1].content
        self.assertIn('"id": "S02"', prompt)
        self.assertIn('"name": "Main benefits"', prompt)
        routes.generate_ad_copies(1, GenerateAdCopyRequest(count=1, structure_id="S03"))
        prompt = self.ai.chat_json.call_args.kwargs["messages"][1].content
        self.assertIn('"id": "S03"', prompt)
        self.assertIn('"name": "Benefits"', prompt)
        self.assertIn("line starting with '- '", prompt)
        self.ai.chat_json.reset_mock()
        for structure_id in ("missing", "default", "classic", "bullet_benefits"):
            with self.subTest(structure_id=structure_id), self.assertRaises(HTTPException) as error:
                routes.generate_ad_copies(1, GenerateAdCopyRequest(structure_id=structure_id))
            self.assertEqual(error.exception.status_code, 404)
        self.ai.chat_json.assert_not_called()

    def test_optional_cta_normalization(self):
        for value in (None, "", "   "):
            self.assertIsNone(AdCopyFields(**self.FIELDS, cta=value).cta)
        result = routes.create_ad_copy(1, AdCopyFields(**self.FIELDS, cta="  Learn more  "))
        self.assertEqual(result["cta"], "Learn more")

    def test_invalid_response_does_not_save_partial_batch(self):
        for payload in (
            {"copies": [self.FIELDS, {**self.FIELDS, "headline": "  "}]},
            {"copies": [self.FIELDS, {**self.FIELDS, "offer_profile_id": 2}]},
            {"copies": [self.FIELDS]},
            {"copies": [self.FIELDS, {**self.FIELDS, "cta": {"button": "go"}}]},
        ):
            with self.subTest(payload=payload):
                self.ai.chat_json.return_value = payload
                with self.assertRaises(HTTPException) as error:
                    routes.generate_ad_copies(1, GenerateAdCopyRequest(count=2))
                self.assertEqual(error.exception.status_code, 502)
                self.assertEqual(self.db.query(AdCopy).count(), 0)

    def test_edit_delete_and_profile_cascade(self):
        created = routes.create_ad_copy(1, AdCopyFields(**self.FIELDS))
        updated = routes.update_ad_copy(created["id"], UpdateAdCopyRequest(**{**self.FIELDS, "headline": "New headline"}, cta="Read more"))
        self.assertEqual(updated["headline"], "New headline")
        self.assertEqual(updated["cta"], "Read more")
        self.assertTrue(routes.delete_ad_copy(created["id"])["deleted"])
        self.assertEqual(routes.list_ad_copies(1), [])
        routes.create_ad_copy(1, AdCopyFields(**self.FIELDS))
        self.db.execute(text("DELETE FROM offer_profiles WHERE id=1"))
        self.db.commit()
        self.assertEqual(self.db.query(AdCopy).count(), 0)

    def test_review_state_persists_and_content_changes_require_review_again(self):
        created = routes.create_ad_copy(1, AdCopyFields(**self.FIELDS))
        self.assertFalse(created["is_reviewed"])

        approved = routes.update_ad_copy(created["id"], UpdateAdCopyRequest(**self.FIELDS, is_reviewed=True))
        self.assertTrue(approved["is_reviewed"])
        self.assertTrue(routes.list_ad_copies(1)[0]["is_reviewed"])

        changed = routes.update_ad_copy(created["id"], UpdateAdCopyRequest(
            **{**self.FIELDS, "headline": "Revised headline"}, is_reviewed=True,
        ))
        self.assertFalse(changed["is_reviewed"])
        approved = routes.update_ad_copy(created["id"], UpdateAdCopyRequest(
            **{**self.FIELDS, "headline": "Revised headline"}, is_reviewed=True,
        ))
        self.assertTrue(approved["is_reviewed"])
        unapproved = routes.update_ad_copy(created["id"], UpdateAdCopyRequest(
            **{**self.FIELDS, "headline": "Revised headline"}, is_reviewed=False,
        ))
        self.assertFalse(unapproved["is_reviewed"])

    def test_missing_entities(self):
        for action in (
            lambda: routes.list_ad_copies(999),
            lambda: routes.create_ad_copy(999, AdCopyFields(**self.FIELDS)),
            lambda: routes.update_ad_copy(999, UpdateAdCopyRequest(**self.FIELDS)),
            lambda: routes.delete_ad_copy(999),
        ):
            with self.assertRaises(HTTPException) as error:
                action()
            self.assertEqual(error.exception.status_code, 404)
        self.composer.compose.side_effect = LookupError("Missing profile")
        with self.assertRaises(HTTPException) as error:
            routes.generate_ad_copies(999, GenerateAdCopyRequest())
        self.assertEqual(error.exception.status_code, 404)
        self.ai.chat_json.assert_not_called()

    def test_request_validation(self):
        for values in ({"count": 0}, {"count": 11}, {"generation_instructions": "x" * 4001}):
            with self.assertRaises(ValidationError):
                GenerateAdCopyRequest(**values)
        with self.assertRaises(ValidationError):
            AdCopyFields(**{**self.FIELDS, "name": " "})

    def test_startup_creates_table(self):
        self.db.close()
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE ad_copies"))
        with patch.object(migrations, "engine", self.engine):
            migrations.init_db()
        columns = {column["name"] for column in inspect(self.engine).get_columns("ad_copies")}
        self.assertTrue({"id", "offer_profile_id", "name", "primary_text", "headline", "description", "cta", "is_reviewed"} <= columns)

    def test_migration_marks_existing_copies_as_unreviewed(self):
        self.db.close()
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE ad_copies"))
            conn.execute(text("""
                CREATE TABLE ad_copies (
                    id INTEGER PRIMARY KEY, offer_profile_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL, primary_text TEXT NOT NULL,
                    headline TEXT NOT NULL, description TEXT NOT NULL, cta TEXT
                )
            """))
            conn.execute(text("""
                INSERT INTO ad_copies (id, offer_profile_id, name, primary_text, headline, description)
                VALUES (1, 1, 'Existing', 'Text', 'Headline', 'Description')
            """))
        with patch.object(migrations, "engine", self.engine):
            migrations._add_missing_is_reviewed_columns()
            migrations._add_missing_is_reviewed_columns()
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT name, is_reviewed FROM ad_copies WHERE id = 1")).one()
        self.assertEqual(row, ("Existing", 0))

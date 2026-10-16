import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session

from api.routes import ad_concepts_routes as routes
from application.dtos.ad_concepts.ad_concept_fields import AdConceptFields, GenerateAdConceptsRequest
from application.services.llm_context_composer import ContextRef, ContextSelection
from application.services.marketing_angle_service import MarketingAngleService
from application.handlers.ad_concepts import generate_ad_concepts_handler as generation
from domain.enums.context_type import ContextType
from domain.enums.ad_formats import AdFormats
from domain.models import models
from domain.models.ad.ad_concept import AdConcept
from domain.models.offer.offer_profile import OfferProfile
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource
from domain.models.offer.marketing_angle import MarketingAngle
from infrastructure.database.db import Base
from infrastructure.database import init_db as migration
from infrastructure.repositories.ad_concepts_repository import AdConceptsRepository
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository
from infrastructure.repositories.marketing_angles_repository import MarketingAnglesRepository


class AdConceptTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add(OfferRaw(id=1, name="Product"))
        self.db.flush()
        self.db.add(OfferSource(id=1, offer_id=1, offer_details="Source"))
        self.db.flush()
        self.db.add(OfferProfile(id=1, offer_source_id=1, name="Profile"))
        self.db.add(OfferProfile(id=2, offer_source_id=1, name="Other profile"))
        self.db.flush()
        self.db.add_all([
            MarketingAngle(id=1, offer_profile_id=1, name="Emotional angle", description="Appeal to care"),
            MarketingAngle(id=2, offer_profile_id=2, name="Foreign angle", description="Not available here"),
            MarketingAngle(id=3, offer_profile_id=1, name="Practical angle", description="Practical value"),
        ])
        self.db.commit()
        self.repository = AdConceptsRepository(None, self.db)
        self.response = {"concepts": [{
            "name": "Unboxing", "description": "Show the product being opened",
            "format": "video", "core_idea": "Reveal the product",
            "key_message": "See what is included",
        }]}
        self.responses = []
        self.messages = []
        self.options = []
        self.context_calls = []

        def compose(*, root, include):
            self.context_calls.append((root, include))
            return "<offer_profile>Profile</offer_profile>\n<offer_source>Source</offer_source>"

        def chat(*, messages, **kwargs):
            self.messages.extend(messages)
            self.options.append(kwargs)
            return self.responses.pop(0) if self.responses else self.response

        container = SimpleNamespace(
            offer_profiles_repository=lambda: OfferProfilesRepository(None, self.db),
            ad_concepts_repository=lambda: self.repository,
            marketing_angles_repository=lambda: MarketingAnglesRepository(None, self.db),
            marketing_angle_service=lambda: MarketingAngleService(MarketingAnglesRepository(None, self.db)),
            llm_context_composer=lambda: SimpleNamespace(compose=compose),
            ai_service=lambda: SimpleNamespace(chat_json=chat),
        )
        for name in ("list_ad_concepts_handler", "generate_ad_concepts_handler", "create_ad_concept_handler", "update_ad_concept_handler", "delete_ad_concept_handler"):
            patcher = patch(f"application.handlers.ad_concepts.{name}.Container", lambda: container)
            patcher.start()
            self.addCleanup(patcher.stop)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_generation_uses_profile_and_source_without_audiences(self):
        result = routes.generate_ad_concepts(1, GenerateAdConceptsRequest(count=1, generation_instructions="Show the package"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["format"], "video")
        self.assertEqual(result[0]["generation_mode"], "standard")
        self.assertEqual(result[0]["marketing_angle_ids"], [])
        self.assertFalse(result[0]["is_reviewed"])
        self.assertEqual(self.context_calls[0], (
            ContextRef(ContextType.OFFER_PROFILE, 1),
            [ContextSelection(ContextType.OFFER_SOURCE)],
        ))
        self.assertIn("Show the package", self.messages[1].content)
        self.assertIn("<offer_source>Source</offer_source>", self.messages[1].content)
        self.assertNotIn("rule_sets", self.options[0])
        self.assertEqual(len(routes.list_ad_concepts(1)), 1)

    def test_invalid_output_does_not_save_partial_results(self):
        self.response["concepts"][0]["format"] = "carousel"
        with self.assertRaises(HTTPException) as invalid:
            routes.generate_ad_concepts(1, GenerateAdConceptsRequest(count=1))
        self.assertEqual(invalid.exception.status_code, 502)
        self.assertEqual(self.db.query(AdConcept).count(), 0)
        with self.assertRaises(ValidationError):
            AdConceptFields(**self.response["concepts"][0])

    def test_ai_chooses_format_from_instructions_without_explicit_preference(self):
        image = {**self.response["concepts"][0], "format": "image"}
        self.responses = [{"concepts": [image]}]
        result = routes.generate_ad_concepts(1, GenerateAdConceptsRequest(count=1, generation_instructions="Daj img"))
        self.assertEqual(result[0]["format"], "image")
        self.assertEqual(len(self.options), 1)
        self.assertIn("Daj img", self.messages[1].content)
        self.assertIn("Choose image or video according to the user's instructions", self.messages[1].content)
        self.assertNotIn("FORMAT REQUIREMENT", self.messages[1].content)
        self.assertNotIn('"format": "video"', generation.SYSTEM_PROMPT)

    def test_rejects_repeated_wrong_format_without_saving(self):
        with self.assertRaises(HTTPException) as error:
            routes.generate_ad_concepts(1, GenerateAdConceptsRequest(count=1, preferred_format="image"))
        self.assertEqual(error.exception.status_code, 502)
        self.assertEqual(len(self.options), 2)
        self.assertEqual(self.db.query(AdConcept).count(), 0)
        self.assertIn('FORMAT REQUIREMENT: Every concept must have format "image"', self.messages[1].content)

    def test_generation_with_selected_marketing_angle_persists_relation(self):
        result = routes.generate_ad_concepts(1, GenerateAdConceptsRequest(count=1, marketing_angle_id=1))
        self.assertEqual(result[0]["marketing_angle_ids"], [1])
        self.assertEqual(self.context_calls[0][1], [
            ContextSelection(ContextType.OFFER_SOURCE),
            ContextSelection(ContextType.MARKETING_ANGLE, include_ids=(1,)),
        ])
        with self.assertRaises(HTTPException) as foreign:
            routes.create_ad_concept(1, routes.CreateAdConceptRequest(
                **self.response["concepts"][0], marketing_angle_id=2,
            ))
        self.assertEqual(foreign.exception.status_code, 422)
        self.db.delete(self.db.get(MarketingAngle, 1))
        self.db.commit()
        self.db.expire_all()
        self.assertEqual(self.db.get(AdConcept, result[0]["id"]).marketing_angles, [])

    def test_experimental_uses_multiple_equal_angles_and_rejects_incompatible_selection(self):
        request = GenerateAdConceptsRequest(
            count=1, generation_mode="experimental", marketing_angle_ids=[1, 3],
        )
        result = routes.generate_ad_concepts(1, request)
        self.assertEqual(result[0]["generation_mode"], "experimental")
        self.assertEqual(result[0]["marketing_angle_ids"], [1, 3])
        self.assertEqual(self.context_calls[0][1][-1], ContextSelection(
            ContextType.MARKETING_ANGLE, include_ids=(1, 3),
        ))
        self.assertIn("Treat all selected marketing angles as equal", self.messages[1].content)
        self.response = {"concepts": []}
        with self.assertRaises(HTTPException) as incompatible:
            routes.generate_ad_concepts(1, request)
        self.assertEqual(incompatible.exception.status_code, 422)
        self.assertEqual(self.db.query(AdConcept).count(), 1)
        with self.assertRaises(HTTPException) as foreign:
            routes.generate_ad_concepts(1, GenerateAdConceptsRequest(
                count=1, generation_mode="experimental", marketing_angle_ids=[1, 2],
            ))
        self.assertEqual(foreign.exception.status_code, 422)

    def test_mode_selection_validation(self):
        self.assertEqual(AdConceptFields(**self.response["concepts"][0]).format, AdFormats.VIDEO)
        self.assertEqual(
            GenerateAdConceptsRequest(preferred_format="image").preferred_format,
            AdFormats.IMAGE,
        )
        for payload in (
            {"generation_mode": "standard", "marketing_angle_ids": [1, 3]},
            {"generation_mode": "experimental", "marketing_angle_ids": []},
            {"generation_mode": "experimental", "marketing_angle_ids": [1, 1]},
        ):
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                GenerateAdConceptsRequest(**payload)
        self.assertEqual(
            GenerateAdConceptsRequest(generation_mode="experimental", marketing_angle_ids=[1]).marketing_angle_ids,
            [1],
        )

    def test_create_update_delete(self):
        fields = routes.CreateAdConceptRequest(**self.response["concepts"][0], marketing_angle_id=1)
        created = routes.create_ad_concept(1, fields)
        self.assertEqual(created["marketing_angle_ids"], [1])
        updated = routes.update_ad_concept(created["id"], routes.UpdateAdConceptRequest(**fields.model_dump(), is_reviewed=True))
        self.assertTrue(updated["is_reviewed"])
        changed = routes.update_ad_concept(created["id"], routes.UpdateAdConceptRequest(**{**fields.model_dump(), "core_idea": "Different idea"}, is_reviewed=True))
        self.assertFalse(changed["is_reviewed"])
        experimental = routes.update_ad_concept(created["id"], routes.UpdateAdConceptRequest(
            **{**fields.model_dump(exclude={"generation_mode", "marketing_angle_ids"}),
               "generation_mode": "experimental", "marketing_angle_ids": [1, 3]},
            is_reviewed=True,
        ))
        self.assertEqual(experimental["marketing_angle_ids"], [1, 3])
        self.assertFalse(experimental["is_reviewed"])
        reviewed = routes.update_ad_concept(created["id"], routes.UpdateAdConceptRequest(
            **self.response["concepts"][0],
            is_reviewed=True,
        ))
        self.assertTrue(reviewed["is_reviewed"])
        self.assertEqual(reviewed["generation_mode"], "experimental")
        self.assertEqual(reviewed["marketing_angle_ids"], [1, 3])
        routes.delete_ad_concept(created["id"])
        self.assertEqual(routes.list_ad_concepts(1), [])

    def test_existing_angle_relation_is_migrated_idempotently(self):
        self.db.close()
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE ad_concepts"))
            conn.execute(text(
                "CREATE TABLE ad_concepts (id INTEGER PRIMARY KEY, "
                "offer_profile_id INTEGER NOT NULL REFERENCES offer_profiles(id), "
                "name VARCHAR(255) NOT NULL, description TEXT NOT NULL, "
                "format VARCHAR(16) NOT NULL, core_idea TEXT NOT NULL, "
                "key_message TEXT NOT NULL, "
                "marketing_angle_id INTEGER REFERENCES marketing_angles(id))"
            ))
            conn.execute(text(
                "INSERT INTO ad_concepts (id, offer_profile_id, name, description, format, core_idea, key_message, marketing_angle_id) "
                "VALUES (1, 1, 'Existing', 'Description', 'image', 'Idea', 'Message', 1)"
            ))
        with patch.object(migration, "engine", self.engine):
            migration._migrate_ad_concept_modes_and_angles()
            migration._migrate_ad_concept_modes_and_angles()
        self.assertIn("generation_mode", {
            column["name"] for column in inspect(self.engine).get_columns("ad_concepts")
        })
        self.assertNotIn("marketing_angle_id", {
            column["name"] for column in inspect(self.engine).get_columns("ad_concepts")
        })
        with self.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT generation_mode FROM ad_concepts WHERE id=1")).scalar_one(), "standard")
            self.assertEqual(conn.execute(text("SELECT marketing_angle_id FROM ad_concept_marketing_angles WHERE ad_concept_id=1")).scalars().all(), [1])


if __name__ == "__main__":
    unittest.main()

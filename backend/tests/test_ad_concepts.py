import json
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
from domain.enums.context_type import ContextType
from domain.enums.llm_rule_set import LlmRuleSet
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
        self.db.add(OfferSource(id=1, offer_id=1, offer_summary="Source"))
        self.db.flush()
        self.db.add(OfferProfile(id=1, offer_source_id=1, name="Profile"))
        self.db.add(OfferProfile(id=2, offer_source_id=1, name="Other profile"))
        self.db.flush()
        self.db.add_all([
            MarketingAngle(id=1, offer_profile_id=1, name="Emotional angle", description="Appeal to care"),
            MarketingAngle(id=2, offer_profile_id=2, name="Foreign angle", description="Not available here"),
        ])
        self.db.commit()
        self.repository = AdConceptsRepository(None, self.db)
        self.response = {"concepts": [{
            "name": "Unboxing", "description": "Show the product being opened",
            "format": "video", "core_idea": "Reveal the product",
            "key_message": "See what is included",
        }]}
        self.messages = []
        self.options = []
        self.context_calls = []

        def compose(*, root, include):
            self.context_calls.append((root, include))
            return "<offer_profile>Profile</offer_profile>\n<offer_source>Source</offer_source>"

        def chat(*, messages, **kwargs):
            self.messages.extend(messages)
            self.options.append(kwargs)
            return SimpleNamespace(content=json.dumps(self.response))

        container = SimpleNamespace(
            offer_profiles_repository=lambda: OfferProfilesRepository(None, self.db),
            ad_concepts_repository=lambda: self.repository,
            marketing_angles_repository=lambda: MarketingAnglesRepository(None, self.db),
            llm_context_composer=lambda: SimpleNamespace(compose=compose),
            ai_service=lambda: SimpleNamespace(chat_llm=chat),
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
        self.assertFalse(result[0]["is_reviewed"])
        self.assertEqual(self.context_calls[0], (
            ContextRef(ContextType.OFFER_PROFILE, 1),
            [ContextSelection(ContextType.OFFER_SOURCE)],
        ))
        self.assertIn("Show the package", self.messages[1].content)
        self.assertIn("<offer_source>Source</offer_source>", self.messages[1].content)
        self.assertEqual(self.options[0]["rule_sets"], (LlmRuleSet.JSON_OUTPUT, LlmRuleSet.ENGLISH_OUTPUT))
        self.assertEqual(len(routes.list_ad_concepts(1)), 1)

    def test_invalid_output_does_not_save_partial_results(self):
        self.response["concepts"][0]["format"] = "carousel"
        with self.assertRaises(HTTPException) as invalid:
            routes.generate_ad_concepts(1, GenerateAdConceptsRequest(count=1))
        self.assertEqual(invalid.exception.status_code, 502)
        self.assertEqual(self.db.query(AdConcept).count(), 0)
        with self.assertRaises(ValidationError):
            AdConceptFields(**self.response["concepts"][0])

    def test_generation_with_selected_marketing_angle_persists_relation(self):
        result = routes.generate_ad_concepts(1, GenerateAdConceptsRequest(count=1, marketing_angle_id=1))
        self.assertEqual(result[0]["marketing_angle_id"], 1)
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
        self.assertIsNone(self.db.get(AdConcept, result[0]["id"]).marketing_angle_id)

    def test_create_update_delete(self):
        fields = routes.CreateAdConceptRequest(**self.response["concepts"][0], marketing_angle_id=1)
        created = routes.create_ad_concept(1, fields)
        self.assertEqual(created["marketing_angle_id"], 1)
        updated = routes.update_ad_concept(created["id"], routes.UpdateAdConceptRequest(**fields.model_dump(), is_reviewed=True))
        self.assertTrue(updated["is_reviewed"])
        changed = routes.update_ad_concept(created["id"], routes.UpdateAdConceptRequest(**{**fields.model_dump(), "core_idea": "Different idea"}, is_reviewed=True))
        self.assertFalse(changed["is_reviewed"])
        routes.delete_ad_concept(created["id"])
        self.assertEqual(routes.list_ad_concepts(1), [])

    def test_existing_table_gains_nullable_marketing_angle_relation(self):
        self.db.close()
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE ad_concepts"))
            conn.execute(text(
                "CREATE TABLE ad_concepts (id INTEGER PRIMARY KEY, "
                "offer_profile_id INTEGER NOT NULL REFERENCES offer_profiles(id), "
                "name VARCHAR(255) NOT NULL, description TEXT NOT NULL, "
                "format VARCHAR(16) NOT NULL, core_idea TEXT NOT NULL, "
                "key_message TEXT NOT NULL)"
            ))
            conn.execute(text(
                "INSERT INTO ad_concepts (id, offer_profile_id, name, description, format, core_idea, key_message) "
                "VALUES (1, 1, 'Existing', 'Description', 'image', 'Idea', 'Message')"
            ))
        with patch.object(migration, "engine", self.engine):
            migration._add_ad_concept_marketing_angle()
            migration._add_ad_concept_marketing_angle()
        self.assertIn("marketing_angle_id", {
            column["name"] for column in inspect(self.engine).get_columns("ad_concepts")
        })
        with self.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT marketing_angle_id FROM ad_concepts WHERE id=1")).scalar_one(), None)


if __name__ == "__main__":
    unittest.main()

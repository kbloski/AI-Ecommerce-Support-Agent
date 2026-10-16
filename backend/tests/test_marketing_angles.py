import json
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session

from api.routes import marketing_angles_routes as routes
from domain.models import models
from domain.models.audience.target_audience import TargetAudience
from domain.models.offer.marketing_angle import MarketingAngle
from domain.models.offer.offer_profile import OfferProfile
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource
from infrastructure.database.db import Base
from infrastructure.database import init_db as migration
from infrastructure.repositories.marketing_angles_repository import MarketingAnglesRepository
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository
from infrastructure.repositories.target_audiences_repository import TargetAudiencesRepository
from application.services.target_audience_service import TargetAudienceService
from application.services.offer_service import OfferService
from application.assemblers.offer_assembler import OfferAssembler
from infrastructure.repositories.offers_repository import OffersRepository
from application.handlers.offer_sources import generate_offer_source_handler as source_generation
from application.services.llm_context_composer import LlmContextComposer, ContextRef, ContextSelection
from application.services.marketing_angle_service import MarketingAngleService
from domain.enums.context_type import ContextType


class MarketingAnglesTests(unittest.TestCase):
    ANGLE_FIELDS = {
        "name": "Meaningful gift",
        "description": "Connect the buyer's need for a personal gift to the offer.",
        "core_message": "A personal gift matters",
        "value_proposition": "A more meaningful present",
        "pain_point": "Generic gifts feel impersonal",
        "desire": "Give a memorable gift",
        "emotional_driver": "Care for a loved one",
        "supporting_arguments": ["Personal choice"],
        "proof_points": [],
    }

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
        self.db.add_all([
            OfferProfile(id=1, offer_source_id=1, name="Profile"),
            OfferProfile(id=2, offer_source_id=1, name="Other profile"),
        ])
        self.db.flush()
        self.db.add_all([
            TargetAudience(id=1, offer_profile_id=1, name="Gift buyers", fact_status="unverified"),
            TargetAudience(id=2, offer_profile_id=1, name="Collectors", fact_status="unverified"),
            TargetAudience(id=3, offer_profile_id=2, name="Other audience", fact_status="unverified"),
        ])
        self.db.commit()
        self.repo = MarketingAnglesRepository(None, self.db)
        self.audiences = TargetAudienceService(TargetAudiencesRepository(None, self.db))
        def profile_context(profile_id):
            if self.db.get(OfferProfile, profile_id) is None:
                raise LookupError("Offer profile not found")
            return '<offer_profile>{"name":"Profile"}</offer_profile>'
        self.profile_service = SimpleNamespace(
            build_llm_context=profile_context,
            get_offer_profile_details_by_id=lambda profile_id: self.db.get(OfferProfile, profile_id),
        )
        offers_repository = OffersRepository(None, self.db)
        self.composer = LlmContextComposer(
            self.profile_service,
            self.audiences,
            OfferService(None, offers_repository, OfferAssembler(None, offers_repository)),
            SimpleNamespace(build_llm_context=lambda source_id: f'<offer_source>{source_id}: Source</offer_source>'),
            MarketingAngleService(self.repo),
        )
        self.messages = []
        self.response = {"angles": [self.ANGLE_FIELDS.copy()]}
        self.chat_options = []
        def chat(messages, **kwargs):
            self.messages.extend(messages)
            self.chat_options.append(kwargs)
            return self.response
        self.container = SimpleNamespace(
            offer_profiles_repository=lambda: OfferProfilesRepository(None, self.db),
            marketing_angles_repository=lambda: self.repo,
            target_audiences_repository=lambda: TargetAudiencesRepository(None, self.db),
            target_audience_service=lambda: self.audiences,
            offer_profile_service=lambda: self.profile_service,
            llm_context_composer=lambda: self.composer,
            ai_service=lambda: SimpleNamespace(chat_json=chat),
        )
        for name in ("list_marketing_angles_handler", "generate_marketing_angles_handler", "create_marketing_angle_handler", "update_marketing_angle_handler", "delete_marketing_angle_handler"):
            patcher = patch(f"application.handlers.marketing_angles.{name}.Container", lambda: self.container)
            patcher.start()
            self.addCleanup(patcher.stop)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_generation_uses_only_selected_audiences_and_instructions(self):
        payload = routes.GenerateMarketingAnglesRequest(count=1, target_audience_ids=[1], generation_instructions="Focus on emotional value")
        result = routes.generate_marketing_angles(1, payload)
        listed = routes.list_marketing_angles(1)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(listed), 1)
        self.assertFalse(result[0]["is_reviewed"])
        self.assertEqual(result[0]["core_message"], "A personal gift matters")
        self.assertEqual(result[0]["supporting_arguments"], ["Personal choice"])
        self.assertEqual(result[0]["proof_points"], [])
        prompt = self.messages[1].content
        self.assertIn("Gift buyers", prompt)
        self.assertIn("<offer_source>1: Source</offer_source>", prompt)
        self.assertNotIn("Collectors", prompt)
        self.assertNotIn("Other audience", prompt)
        self.assertIn("Focus on emotional value", prompt)
        self.assertIn("exactly 1", prompt)
        self.assertNotIn("rule_sets", self.chat_options[0])
        combined = self.composer.compose(
            ContextRef(ContextType.OFFER_PROFILE, 1),
            [ContextSelection(ContextType.TARGET_AUDIENCES, include_ids=(1,))],
        )
        self.assertLess(combined.index("<offer_profile>"), combined.index("<target_audiences"))
        with_source = self.composer.compose(
            ContextRef(ContextType.OFFER_PROFILE, 1),
            [ContextSelection(ContextType.OFFER_SOURCE)],
        )
        self.assertIn("<offer_source>1: Source</offer_source>", with_source)
        self.assertEqual(self.composer.compose(ContextRef(ContextType.OFFER_PROFILE, 1)), '<offer_profile>{"name":"Profile"}</offer_profile>')
        context = ET.fromstring(self.audiences.build_llm_context(1, [1]))
        self.assertEqual(context.tag, "target_audiences")
        self.assertEqual([item["name"] for item in json.loads(context.text)], ["Gift buyers"])
        self.assertNotIn("id", json.loads(context.text)[0])
        with self.assertRaises(ValueError):
            self.audiences.build_llm_context(1, [1, 1])
        with self.assertRaises(ValueError):
            self.audiences.build_llm_context(1, [3])
        with self.assertRaises(LookupError):
            self.audiences.get_target_audience_details_by_id(999)

    def test_rejects_foreign_audience_and_partial_model_output(self):
        with self.assertRaises(HTTPException) as foreign:
            routes.generate_marketing_angles(1, routes.GenerateMarketingAnglesRequest(count=1, target_audience_ids=[3]))
        self.assertEqual(foreign.exception.status_code, 422)
        with self.assertRaises(HTTPException) as incomplete:
            routes.generate_marketing_angles(1, routes.GenerateMarketingAnglesRequest(count=2))
        self.assertEqual(incomplete.exception.status_code, 502)
        self.response = {"angles": [{"name": "Missing fields", "description": "Too short"}]}
        with self.assertRaises(HTTPException) as malformed:
            routes.generate_marketing_angles(1, routes.GenerateMarketingAnglesRequest(count=1))
        self.assertEqual(malformed.exception.status_code, 502)
        self.assertEqual(self.db.query(MarketingAngle).count(), 0)

    def test_composer_skips_empty_audiences_and_rejects_invalid_selections(self):
        root = ContextRef(ContextType.OFFER_PROFILE, 1)
        empty = self.composer.compose(root, [ContextSelection(ContextType.TARGET_AUDIENCES, include_ids=())])
        self.assertNotIn("target_audiences", empty)
        all_audiences = self.composer.compose(root, [ContextSelection(ContextType.TARGET_AUDIENCES)])
        self.assertIn("Gift buyers", all_audiences)
        self.assertIn("Collectors", all_audiences)
        self.assertNotIn("Other audience", all_audiences)
        excluded = self.composer.compose(root, [ContextSelection(ContextType.TARGET_AUDIENCES, exclude_ids=(2,))])
        self.assertIn("Gift buyers", excluded)
        self.assertNotIn("Collectors", excluded)
        selected_and_excluded = self.composer.compose(root, [ContextSelection(ContextType.TARGET_AUDIENCES, include_ids=(1, 2), exclude_ids=(1,))])
        self.assertNotIn("Gift buyers", selected_and_excluded)
        self.assertIn("Collectors", selected_and_excluded)
        with self.assertRaises(ValueError):
            self.composer.compose(root, [ContextSelection(ContextType.TARGET_AUDIENCES, include_ids=(3,))])
        with self.assertRaises(ValueError):
            self.composer.compose(root, [ContextSelection(ContextType.TARGET_AUDIENCES, include_ids=(1, 1))])
        with self.assertRaises(ValueError):
            self.composer.compose(root, [ContextSelection(ContextType.TARGET_AUDIENCES, exclude_ids=(3,))])
        with self.assertRaises(LookupError):
            self.composer.compose(ContextRef(ContextType.OFFER_PROFILE, 999))
        with self.assertRaises(HTTPException) as missing:
            routes.generate_marketing_angles(999, routes.GenerateMarketingAnglesRequest(count=1))
        self.assertEqual(missing.exception.status_code, 404)

    def test_composer_includes_only_selected_profile_marketing_angle(self):
        self.db.add_all([
            MarketingAngle(id=10, offer_profile_id=1, name="Selected", description="Buyer perspective"),
            MarketingAngle(id=12, offer_profile_id=1, name="Second", description="Another perspective"),
            MarketingAngle(id=11, offer_profile_id=2, name="Foreign", description="Other perspective"),
        ])
        self.db.commit()
        root = ContextRef(ContextType.OFFER_PROFILE, 1)
        context = self.composer.compose(root, [ContextSelection(ContextType.MARKETING_ANGLE, include_ids=(10,))])
        self.assertIn('"name": "Selected"', context)
        combined = self.composer.compose(root, [ContextSelection(ContextType.MARKETING_ANGLE, include_ids=(10, 12))])
        self.assertIn('"id": 10', combined)
        self.assertIn('"id": 12', combined)
        self.assertNotIn("Foreign", context)
        with self.assertRaises(ValueError):
            self.composer.compose(root, [ContextSelection(ContextType.MARKETING_ANGLE, include_ids=(10, 10))])
        with self.assertRaises(ValueError):
            self.composer.compose(root, [ContextSelection(ContextType.MARKETING_ANGLE, include_ids=(11,))])
        with self.assertRaises(LookupError):
            self.composer.compose(root, [ContextSelection(ContextType.MARKETING_ANGLE, include_ids=(999,))])

    def test_offer_source_generator_uses_raw_offer_context(self):
        raw_context = self.composer.compose(ContextRef(ContextType.OFFER_RAW, 1))
        self.assertIn('"name": "Product"', raw_context)
        self.assertNotIn("offer_profile", raw_context)
        with self.assertRaises(LookupError):
            self.composer.compose(ContextRef(ContextType.OFFER_RAW, 999))
        with self.assertRaises(ValueError):
            self.composer.compose(
                ContextRef(ContextType.OFFER_RAW, 1),
                [ContextSelection(ContextType.TARGET_AUDIENCES)],
            )
        self.response = {"offer_details": "Generated source", "offer_elements": []}
        with patch.object(source_generation, "Container", lambda: self.container), patch.object(source_generation, "SessionLocal", lambda: Session(self.engine)):
            result = source_generation.generate_offer_source_handler(1)
        self.assertEqual(result.offer_details, "Generated source")
        self.assertIn('"name": "Product"', self.messages[1].content)
        self.assertNotIn("target_audiences", self.messages[1].content)

    def test_offer_source_generator_passes_instructions_to_both_stages(self):
        self.response = {"offer_details": "Generated source", "offer_elements": []}
        with patch.object(source_generation, "Container", lambda: self.container), patch.object(source_generation, "SessionLocal", lambda: Session(self.engine)):
            result = source_generation.generate_offer_source_handler(
                1, generation_instructions="  Focus on technical specifications  "
            )
        self.assertEqual(result.offer_details, "Generated source")
        instructions = [message for message in self.messages if "<generation_instructions>" in message.content]
        self.assertEqual(len(instructions), 2)
        for message in instructions:
            self.assertIn("\nFocus on technical specifications\n", message.content)
            self.assertIn("do not invent offer facts", message.content)

    def test_create_update_delete_and_profile_cascade(self):
        created = routes.create_marketing_angle(1, routes.MarketingAngleFields(**{**self.ANGLE_FIELDS, "name": "Angle"}))
        updated = routes.update_marketing_angle(created["id"], routes.UpdateMarketingAngleRequest(**{**self.ANGLE_FIELDS, "name": "Angle"}, is_reviewed=True))
        self.assertTrue(updated["is_reviewed"])
        changed_field = routes.update_marketing_angle(created["id"], routes.UpdateMarketingAngleRequest(**{**self.ANGLE_FIELDS, "name": "Angle", "core_message": "New core message"}, is_reviewed=True))
        self.assertFalse(changed_field["is_reviewed"])
        changed = routes.update_marketing_angle(created["id"], routes.UpdateMarketingAngleRequest(**{**self.ANGLE_FIELDS, "name": "New angle"}, is_reviewed=True))
        self.assertFalse(changed["is_reviewed"])
        routes.delete_marketing_angle(created["id"])
        self.assertEqual(routes.list_marketing_angles(1), [])
        routes.create_marketing_angle(1, routes.MarketingAngleFields(**{**self.ANGLE_FIELDS, "name": "Cascade"}))
        self.db.delete(self.db.get(OfferProfile, 1))
        self.db.commit()
        self.assertEqual(self.db.query(MarketingAngle).count(), 0)

    def test_existing_angles_gain_new_fields_without_losing_rows(self):
        self.db.close()
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE marketing_angles"))
            conn.execute(text("CREATE TABLE marketing_angles (id INTEGER PRIMARY KEY, offer_profile_id INTEGER NOT NULL REFERENCES offer_profiles(id), name VARCHAR(255) NOT NULL, description TEXT NOT NULL, is_reviewed BOOLEAN NOT NULL DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"))
            conn.execute(text("INSERT INTO marketing_angles (id, offer_profile_id, name, description) VALUES (1, 1, 'Existing', 'Keep this')"))
        with patch.object(migration, "engine", self.engine):
            migration._add_marketing_angle_fields()
            migration._add_marketing_angle_fields()
        columns = {column["name"] for column in inspect(self.engine).get_columns("marketing_angles")}
        self.assertTrue(set(self.ANGLE_FIELDS) <= columns)
        self.db = Session(self.engine)
        angle = self.db.get(MarketingAngle, 1)
        self.assertEqual(angle.description, "Keep this")
        self.assertEqual(angle.core_message, "")
        self.assertEqual(angle.supporting_arguments, [])
        self.assertEqual(angle.proof_points, [])


if __name__ == "__main__":
    unittest.main()

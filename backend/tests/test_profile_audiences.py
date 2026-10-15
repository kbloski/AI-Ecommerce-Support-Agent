import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session
from infrastructure.database.db import Base
from infrastructure.database import init_db as migration
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository
from infrastructure.repositories.target_audiences_repository import TargetAudiencesRepository
from infrastructure.repositories.additional_contexts_repository import AdditionalContextsRepository
from application.services.offer_profile_service import OfferProfileService
from application.services.llm_context_composer import LlmContextComposer, ContextRef
from application.services.target_audience_service import TargetAudienceService
from domain.enums.context_type import ContextType
from domain.enums.llm_rule_set import LlmRuleSet
from application.assemblers.offer_profile_assembler import OfferProfileAssembler
import xml.etree.ElementTree as ET
from application.handlers.target_audience import generate_target_audience_handler as generation
from application.handlers.target_audience import get_target_audience_handler as listing
from domain.models import models
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource
from domain.models.offer.offer_profile import OfferProfile
from domain.models.audience.target_audience import TargetAudience
from domain.models.context.additional_context import AdditionalContext


class ProfileAudienceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        @event.listens_for(self.engine, "connect")
        def fk(connection, record): connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add(OfferRaw(id=1, name="Product")); self.db.flush()
        self.db.add_all([OfferSource(id=id, offer_id=1, offer_summary="Source") for id in (1, 2, 3)]); self.db.flush()
        self.db.add_all([OfferProfile(id=1, offer_source_id=1, name="Business buyers"), OfferProfile(id=2, offer_source_id=2, name="A"), OfferProfile(id=3, offer_source_id=2, name="B")]); self.db.commit()
        self.repo = TargetAudiencesRepository(None, self.db)

    def tearDown(self): self.db.close(); self.engine.dispose()

    def test_migration_preserves_rows_and_handles_ambiguous_sources(self):
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE target_audiences"))
            conn.execute(text("""CREATE TABLE target_audiences (id INTEGER PRIMARY KEY, offer_source_id INTEGER REFERENCES offer_sources(id), name VARCHAR NOT NULL, fact_status VARCHAR NOT NULL, is_reviewed BOOLEAN NOT NULL DEFAULT 0)"""))
            conn.execute(text("INSERT INTO target_audiences VALUES (1,1,'One','unverified',1),(2,2,'Two','unverified',0),(3,3,'Three','unverified',0)"))
        with patch.object(migration, "engine", self.engine):
            migration._migrate_target_audiences_to_offer_profiles()
            migration._migrate_target_audiences_to_offer_profiles()
            migration.init_db()
        self.db.expire_all()
        rows = self.db.query(TargetAudience).order_by(TargetAudience.id).all()
        self.assertEqual([r.name for r in rows], ["One", "Two", "Three"])
        self.assertEqual(rows[0].offer_profile_id, 1)
        self.assertTrue(rows[0].is_reviewed)
        for row, source_id in zip(rows[1:], (2,3)):
            profile = self.db.get(OfferProfile, row.offer_profile_id)
            self.assertEqual(profile.offer_source_id, source_id)
            self.assertEqual(profile.name, "Przeniesione grupy docelowe")
        self.assertEqual(inspect(self.engine).get_foreign_keys("target_audiences")[0]["referred_table"], "offer_profiles")
        with self.engine.connect() as conn: self.assertFalse(conn.execute(text("PRAGMA foreign_key_check")).fetchall())

    def test_removed_fields_migration_preserves_remaining_audience_data(self):
        self.db.add(TargetAudience(id=1, offer_profile_id=1, name="Keep audience", fact_status="unverified", age_min=30, is_reviewed=True))
        self.db.commit()
        removed = {"message_angles", "marketing_channels", "score", "confidence", "awareness_level", "reason", "decision_time", "research_level", "price_sensitivity", "location", "objections", "purchasing_power"}
        with self.engine.begin() as conn:
            for column in sorted(removed):
                conn.execute(text(f'ALTER TABLE target_audiences ADD COLUMN "{column}" TEXT'))
            conn.execute(text('CREATE INDEX ix_target_audience_score ON target_audiences(score)'))
        with patch.object(migration, "engine", self.engine):
            migration._remove_obsolete_target_audience_columns()
            migration._remove_obsolete_target_audience_columns()
        columns = {column["name"] for column in inspect(self.engine).get_columns("target_audiences")}
        self.assertFalse(removed & columns)
        self.db.expire_all()
        audience = self.db.get(TargetAudience, 1)
        self.assertEqual(audience.name, "Keep audience")
        self.assertEqual(audience.age_min, 30)
        self.assertEqual(audience.offer_profile_id, 1)
        self.assertTrue(audience.is_reviewed)
        from application.mappers.target_audience_mapper import TargetAudienceMapper
        self.assertFalse(removed & set(TargetAudienceMapper.to_dto(audience).to_dict()))

    def test_audience_content_matches_requested_shape(self):
        from application.mappers.target_audience_mapper import TargetAudienceMapper
        expected = {"name": "Audience", "age_min": None, "age_max": None, "gender": None, "lifestyles": [], "values": [], "pain_points": [], "desires": [], "motivations": [], "buying_triggers": []}
        audience = TargetAudience(id=1, offer_profile_id=1, name="Audience", fact_status="unverified", is_reviewed=False)
        self.assertEqual(TargetAudienceMapper.to_dto(audience).to_content_dict(), expected)
        schema = json.loads(generation.get_target_audience_schema())["audiences"][0]
        self.assertEqual(schema, {**expected, "name": ""})

    def test_generation_uses_profile_source_and_attached_information(self):
        contexts = AdditionalContextsRepository(None, self.db)
        contexts.create_for_offer_profile(1, AdditionalContext(name="Guidance", content="Focus on procurement teams"))
        profiles = OfferProfilesRepository(None, self.db)
        service = OfferProfileService(profiles, OfferProfileAssembler(contexts))
        sample = json.loads(generation.get_target_audience_schema())["audiences"][0]
        sample.update(name="Procurement teams")
        self.assertFalse({"message_angles", "marketing_channels", "score", "confidence", "awareness_level", "reason", "decision_time", "research_level", "price_sensitivity", "location", "objections", "purchasing_power"} & set(sample))
        calls = []
        rule_set_calls = []
        def chat(messages, *, rule_sets=()):
            calls.extend(messages)
            rule_set_calls.append(rule_sets)
            return SimpleNamespace(content=json.dumps({"audiences": [sample]}))
        composer = LlmContextComposer(
            service,
            TargetAudienceService(self.repo),
            SimpleNamespace(),
            SimpleNamespace(build_llm_context=lambda source_id: f'<offer_source>{source_id}: Source</offer_source>'),
        )
        container = SimpleNamespace(target_audiences_repository=lambda: self.repo, llm_context_composer=lambda: composer, ai_service=lambda: SimpleNamespace(chat_llm=chat), offer_profiles_repository=lambda: profiles)
        with patch.object(generation, "Container", lambda: container):
            audiences = generation.generate_target_audience_handler(1, count=1, generation_instructions="Focus on procurement decision makers")
        self.assertEqual(audiences[0].offer_profile_id, 1)
        self.assertEqual(rule_set_calls[0], (LlmRuleSet.JSON_OUTPUT, LlmRuleSet.ENGLISH_OUTPUT))
        self.assertIn("exactly 1 target audience", calls[1].content)
        self.assertIn("Business buyers", calls[1].content)
        self.assertIn("Focus on procurement teams", calls[1].content)
        self.assertIn("<offer_source>1: Source</offer_source>", calls[1].content)
        self.assertIn("USER GENERATION INSTRUCTIONS:\nFocus on procurement decision makers", calls[1].content)
        self.assertNotIn("Confirmed", calls[1].content)
        self.assertEqual(composer.compose(ContextRef(ContextType.OFFER_PROFILE, 1)), service.build_llm_context(1))
        context = ET.fromstring(service.build_llm_context(1))
        self.assertEqual(context.tag, "offer_profile")
        self.assertEqual(json.loads(context.text), {"name": "Business buyers", "additional_contexts": [{"name": "Guidance", "content": "Focus on procurement teams"}]})
        details = service.get_offer_profile_details_by_id(1).to_dict()
        self.assertEqual(details["additional_contexts"][0]["name"], "Guidance")
        with patch.object(generation, "Container", lambda: container):
            with self.assertRaisesRegex(Exception, "Expected 2 target audiences"):
                generation.generate_target_audience_handler(1, count=2)
        self.assertEqual(self.db.query(TargetAudience).count(), 1)
        with patch.object(listing, "Container", lambda: container):
            self.assertEqual(listing.get_target_audience_handler(1)["total_items"], 1)
            self.assertEqual(listing.get_target_audience_handler(2)["total_items"], 0)
        self.db.delete(self.db.get(OfferProfile,1)); self.db.commit()
        self.assertEqual(self.db.query(TargetAudience).count(), 0)


if __name__ == "__main__": unittest.main()

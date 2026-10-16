import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session

from application.handlers.ugc_creatives import generate_ugc_creatives_handler as generation
from application.handlers.ugc_creatives import update_ugc_creative_handler as editing
from application.dtos.ugc_creatives.ugc_generation_fields import GenerateUgcRequest
from application.services.llm_context_composer import ContextRef, ContextSelection
from domain.enums.context_type import ContextType
from domain.enums.pipeline_entity_type import PipelineEntityType
from domain.models import models
from domain.models.creative.ugc_creative import UgcCreative
from infrastructure.database.db import Base
from infrastructure.database.ugc_profile_migration import migrate_ugc_to_offer_profiles
from infrastructure.repositories.ugc_creative_repository import UgcCreativeRepository
from application.handlers.pipeline.get_pipeline_path_handler import STAGE_CONFIG


class ProfileUgcTests(unittest.TestCase):
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
        self.repo = UgcCreativeRepository(None, self.db)
        self.ai = Mock()
        self.ai.chat_json.return_value = {"ugc_creatives": [{"name": "Phone demo", "video_flow": ["Opening", "Demonstration"]}]}
        self.composer = Mock()
        self.composer.compose.return_value = "<offer_profile>Profile</offer_profile><offer_source>Source</offer_source>"
        container = SimpleNamespace(
            llm_context_composer=lambda: self.composer,
            ugc_creative_repository=lambda: self.repo,
            ai_service=lambda: self.ai,
        )
        patcher = patch.object(generation, "Container", lambda: container)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.engine.dispose)
        self.addCleanup(self.db.close)

    def test_generation_uses_only_profile_and_offer_source(self):
        result = generation.generate_ugc_creatives_handler(1, GenerateUgcRequest(count=1, generation_instructions="Natural demo"))
        self.composer.compose.assert_called_once_with(
            root=ContextRef(ContextType.OFFER_PROFILE, 1),
            include=[ContextSelection(ContextType.OFFER_SOURCE)],
        )
        self.assertEqual(result[0]["offer_profile_id"], 1)
        self.assertNotIn("message_strategy_id", result[0])
        self.assertFalse(result[0]["is_reviewed"])
        self.assertEqual(self.repo.get_by_offer_profile_id(2), [])
        call = self.ai.chat_json.call_args.kwargs
        self.assertIn("Natural demo", call["messages"][1].content)
        self.assertNotIn("rule_sets", call)

    def test_invalid_output_does_not_save_partial_batch(self):
        self.ai.chat_json.return_value = {"ugc_creatives": [{"name": "Valid"}, {"name": "   "}]}
        with self.assertRaises(HTTPException) as error:
            generation.generate_ugc_creatives_handler(1, GenerateUgcRequest(count=2))
        self.assertEqual(error.exception.status_code, 502)
        self.assertEqual(self.db.query(UgcCreative).count(), 0)

    def test_missing_profile_context_stops_before_generation(self):
        self.composer.compose.side_effect = LookupError("Missing profile")
        with self.assertRaises(HTTPException) as error:
            generation.generate_ugc_creatives_handler(999)
        self.assertEqual(error.exception.status_code, 404)
        self.ai.chat_json.assert_not_called()

    def legacy_table(self):
        self.db.close()
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO brand_marketing (id, offer_source_id) VALUES (1, 1)"))
            conn.execute(text("INSERT INTO marketing_strategy (id, brand_marketing_id) VALUES (1, 1)"))
            conn.execute(text("INSERT INTO offer_strategy (id, marketing_strategy_id) VALUES (1, 1)"))
            conn.execute(text("INSERT INTO message_strategy (id, offer_strategy_id) VALUES (1, 1)"))
            conn.execute(text("DROP TABLE ugc_creatives"))
            conn.execute(text("CREATE TABLE ugc_creatives (id INTEGER PRIMARY KEY, message_strategy_id INTEGER NOT NULL REFERENCES message_strategy(id), name TEXT, video_flow JSON, is_reviewed BOOLEAN DEFAULT 0, is_favorite BOOLEAN DEFAULT 0)"))
            conn.execute(text("INSERT INTO ugc_creatives (id, message_strategy_id, name, video_flow, is_reviewed, is_favorite) VALUES (7, 1, 'Existing UGC', :flow, 1, 1)"), {"flow": '["Original scene"]'})

    def test_migration_preserves_existing_ugc_and_creates_unambiguous_owner(self):
        self.legacy_table()
        migrate_ugc_to_offer_profiles(self.engine)
        migrate_ugc_to_offer_profiles(self.engine)
        with self.engine.begin() as conn:
            row = conn.execute(text("SELECT id, offer_profile_id, video_flow, is_reviewed, is_favorite FROM ugc_creatives")).one()
            self.assertEqual(row[0], 7)
            self.assertNotIn(row[1], (1, 2))
            self.assertEqual(row[2:], ('["Original scene"]', 1, 1))
            self.assertFalse(conn.exec_driver_sql("PRAGMA foreign_key_check").all())
            conn.execute(text("DELETE FROM offer_profiles WHERE id=:id"), {"id": row[1]})
            self.assertEqual(conn.execute(text("SELECT COUNT(*) FROM ugc_creatives")).scalar(), 0)
        self.assertNotIn("message_strategy_id", {c["name"] for c in inspect(self.engine).get_columns("ugc_creatives")})

    def test_unique_profile_receives_legacy_ugc(self):
        self.legacy_table()
        with self.engine.begin() as conn:
            conn.execute(text("DELETE FROM offer_profiles WHERE id=2"))
        migrate_ugc_to_offer_profiles(self.engine)
        self.assertEqual(self.repo.get_by_offer_profile_id(1)[0].id, 7)

    def test_failed_migration_restores_original_data(self):
        self.legacy_table()
        with self.engine.begin() as conn:
            conn.execute(text("CREATE TABLE ugc_creatives_profile_migrated (id INTEGER)"))
        with self.assertRaises(Exception):
            migrate_ugc_to_offer_profiles(self.engine)
        with self.engine.connect() as conn:
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)
            self.assertEqual(conn.execute(text("SELECT name FROM ugc_creatives WHERE id=7")).scalar(), "Existing UGC")

    def test_pipeline_uses_profile_parent(self):
        self.assertEqual(STAGE_CONFIG[PipelineEntityType.UGC_CREATIVE]["parent_field"], "offer_profile_id")
        self.assertEqual(STAGE_CONFIG[PipelineEntityType.UGC_CREATIVE]["parent_stage"], PipelineEntityType.OFFER_PROFILE)

    def test_edit_content_and_reset_review(self):
        item = self.repo.create(UgcCreative(offer_profile_id=1, name="Original", video_flow=["Old scene"], is_reviewed=True))
        container = SimpleNamespace(ugc_creative_repository=lambda: self.repo)
        with patch.object(editing, "Container", lambda: container):
            result = editing.update_ugc_creative_handler(item.id, {
                "name": "Updated", "video_flow": ["New scene"],
                "customer_persona": {"type": "Proposed creator"}, "is_reviewed": True,
            })
            self.assertEqual(result["name"], "Updated")
            self.assertEqual(result["video_flow"], ["New scene"])
            self.assertEqual(result["customer_persona"], {"type": "Proposed creator"})
            self.assertFalse(result["is_reviewed"])
            approved = editing.update_ugc_creative_handler(item.id, {"is_reviewed": True})
            self.assertTrue(approved["is_reviewed"])
            self.assertEqual(approved["name"], "Updated")

    def test_invalid_edit_does_not_change_content_or_owner(self):
        item = self.repo.create(UgcCreative(offer_profile_id=1, name="Original", is_reviewed=True))
        container = SimpleNamespace(ugc_creative_repository=lambda: self.repo)
        with patch.object(editing, "Container", lambda: container):
            for fields in ({"name": " "}, {"name": "Changed", "video_flow": "not a list"}, {"offer_profile_id": 2}, {"is_reviewed": "false"}):
                with self.assertRaises(HTTPException) as error:
                    editing.update_ugc_creative_handler(item.id, fields)
                self.assertEqual(error.exception.status_code, 422)
                self.db.refresh(item)
                self.assertEqual(item.name, "Original")
                self.assertEqual(item.offer_profile_id, 1)
                self.assertTrue(item.is_reviewed)
            with self.assertRaises(HTTPException) as error:
                editing.update_ugc_creative_handler(999, {"name": "Missing"})
            self.assertEqual(error.exception.status_code, 404)

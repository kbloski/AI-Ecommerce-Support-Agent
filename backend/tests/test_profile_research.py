import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session

from domain.models import models
from infrastructure.database.db import Base
from infrastructure.database import init_db as migrations
from infrastructure.database.research_migration import migrate_research_to_offer_profiles
from infrastructure.repositories.checklist_repository import ChecklistRepository
from infrastructure.repositories.offer_profile_analysis_repository import OfferProfileAnalysisRepository
from application.handlers.analysis import offer_profile_analysis_answers_generate_handler as answers
from application.handlers.analysis import analyse_checklist_generate_handler as checklist_generation
from domain.enums.context_type import ContextType


class ProfileResearchTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.addCleanup(self.engine.dispose)

    def seed_legacy(self, profile_count):
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO offers_raw (id, name) VALUES (1, 'Offer')"))
            conn.execute(text("INSERT INTO offer_sources (id, offer_id, offer_details) VALUES (1, 1, 'Details')"))
            for profile in range(1, profile_count + 1):
                conn.execute(text("INSERT INTO offer_profiles (id, offer_source_id, name) VALUES (:id, 1, 'Profile')"), {"id": profile})
            conn.execute(text("DROP TABLE offer_profile_analysis"))
            conn.execute(text("CREATE TABLE offer_source_analysis (offer_source_id INTEGER REFERENCES offer_sources(id), analysis_id INTEGER REFERENCES analysis(id), PRIMARY KEY (offer_source_id, analysis_id))"))
            conn.execute(text("INSERT INTO analysis (id) VALUES (10)"))
            conn.execute(text("INSERT INTO offer_source_analysis VALUES (1, 10)"))
            conn.execute(text("DROP TABLE checklist"))
            conn.execute(text("CREATE TABLE checklist (id INTEGER PRIMARY KEY, offer_source_id INTEGER NOT NULL REFERENCES offer_sources(id), name TEXT NOT NULL, is_favorite BOOLEAN DEFAULT 0, created_at DATETIME, updated_at DATETIME)"))
            conn.execute(text("INSERT INTO checklist (id, offer_source_id, name, is_favorite) VALUES (20, 1, 'Existing checklist', 1)"))
            conn.execute(text("INSERT INTO checklist_item (id, checklist_id, title, is_reviewed) VALUES (30, 20, 'Existing task', 1)"))

    def test_migration_preserves_items_and_is_idempotent(self):
        self.seed_legacy(1)
        migrate_research_to_offer_profiles(self.engine)
        migrate_research_to_offer_profiles(self.engine)
        # Startup migrations must not move the new research relation back to sources.
        with patch.object(migrations, "engine", self.engine):
            migrations._migrate_offer_profiles_to_offer_sources()
            migrations._migrate_checklists_to_offer_sources()
        with Session(self.engine) as session:
            checklists = ChecklistRepository(None, session).find_for_offer_profile(1)
            self.assertEqual([(row.id, row.is_favorite) for row in checklists], [(20, True)])
            self.assertEqual(ChecklistRepository(None, session).find_for_offer_profile(999), [])
            repo = OfferProfileAnalysisRepository(None, session)
            self.assertIsNotNone(repo.find_relation(1, 10))
            self.assertIsNone(repo.find_relation(999, 10))
        with self.engine.begin() as conn:
            self.assertEqual(conn.execute(text("SELECT title, is_reviewed FROM checklist_item WHERE id=30")).one(), ("Existing task", 1))
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_key_check").all(), [])
            conn.execute(text("DELETE FROM offer_profiles WHERE id=1"))
            self.assertEqual(conn.execute(text("SELECT COUNT(*) FROM checklist_item")).scalar(), 0)
        self.assertNotIn("offer_source_analysis", inspect(self.engine).get_table_names())
        self.assertNotIn("offer_source_id", {column["name"] for column in inspect(self.engine).get_columns("checklist")})

    def test_ambiguous_or_missing_profile_gets_dedicated_profile(self):
        self.seed_legacy(2)
        migrate_research_to_offer_profiles(self.engine)
        with self.engine.connect() as conn:
            profile = conn.execute(text("SELECT id FROM offer_profiles WHERE name='Przeniesiony research'")).scalar_one()
            self.assertNotIn(profile, (1, 2))
            self.assertEqual(conn.execute(text("SELECT offer_profile_id FROM checklist")).scalar_one(), profile)
            self.assertEqual(conn.execute(text("SELECT offer_profile_id FROM offer_profile_analysis")).scalar_one(), profile)

    def test_missing_profile_is_created(self):
        self.seed_legacy(0)
        migrate_research_to_offer_profiles(self.engine)
        with self.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT name FROM offer_profiles")).scalar_one(), "Przeniesiony research")

    def test_failed_migration_rolls_back_and_restores_foreign_keys(self):
        self.seed_legacy(1)
        with self.engine.begin() as conn:
            conn.execute(text("CREATE TABLE checklist_research_migrated (id INTEGER)"))
        with self.assertRaises(Exception):
            migrate_research_to_offer_profiles(self.engine)
        with self.engine.connect() as conn:
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)
            self.assertEqual(conn.execute(text("SELECT COUNT(*) FROM offer_source_analysis")).scalar(), 1)
            self.assertEqual(conn.execute(text("SELECT COUNT(*) FROM checklist_item")).scalar(), 1)

    def test_generation_rejects_research_owned_by_another_profile(self):
        container = SimpleNamespace(
            logger=lambda: None,
            ai_service=lambda: None,
            offer_profile_service=lambda: None,
            offer_profile_analysis_repository=lambda: SimpleNamespace(find_relation=lambda **kwargs: None),
            analysis_repository=lambda: None,
            analysis_questions_repository=lambda: None,
            question_answer_repository=lambda: None,
            checklist_repository=lambda: SimpleNamespace(get_by_id=lambda _: SimpleNamespace(offer_profile_id=1)),
            checklist_items_repository=lambda: None,
        )
        with patch.object(answers, "Container", lambda: container), self.assertRaises(LookupError):
            answers.offer_profile_analysis_answers_generate_handler(2, 10)
        with patch.object(checklist_generation, "Container", lambda: container), self.assertRaises(ValueError):
            checklist_generation.analyse_checklist_generate_handler(2, 20)

    def test_both_generators_request_profile_and_source_context(self):
        composer = Mock()
        composer.compose.return_value = "Profile context and source facts"
        ai = Mock()
        ai.chat_llm.return_value = SimpleNamespace(content="[]")
        repository = Mock()
        repository.create_many.return_value = []
        repository.find_relation.return_value = SimpleNamespace(analysis_id=10)
        repository.get_by_id.return_value = SimpleNamespace(id=10, offer_profile_id=2)
        container = SimpleNamespace(
            logger=lambda: Mock(), ai_service=lambda: ai,
            llm_context_composer=lambda: composer,
            offer_profile_analysis_repository=lambda: repository,
            analysis_repository=lambda: repository,
            analysis_questions_repository=lambda: repository,
            question_answer_repository=lambda: repository,
            checklist_repository=lambda: repository,
            checklist_items_repository=lambda: repository,
        )
        with patch.object(answers, "Container", lambda: container):
            answers.offer_profile_analysis_answers_generate_handler(2, 10)
        with patch.object(checklist_generation, "Container", lambda: container):
            checklist_generation.analyse_checklist_generate_handler(2, 20)
        self.assertEqual(composer.compose.call_count, 2)
        for call in composer.compose.call_args_list:
            self.assertEqual(call.kwargs["root"].type, ContextType.OFFER_PROFILE)
            self.assertEqual(call.kwargs["root"].id, 2)
            self.assertEqual(call.kwargs["include"][0].type, ContextType.OFFER_SOURCE)
        for call in ai.chat_llm.call_args_list:
            self.assertIn("Profile context and source facts", call.kwargs["messages"][1].content)

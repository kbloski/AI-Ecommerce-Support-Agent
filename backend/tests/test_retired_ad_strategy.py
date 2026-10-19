import unittest
from unittest.mock import patch

from fastapi import APIRouter
from sqlalchemy import create_engine, event, inspect, text

from api.routes.general_routes import register_general_routes
from domain.models import models
from infrastructure.database import init_db as migration
from infrastructure.database.db import Base
from infrastructure.database.retired_ad_strategy_migration import RETIRED_AD_STRATEGY_TABLES


class RetiredAdStrategyTests(unittest.TestCase):
    def test_init_removes_current_and_legacy_storage_and_preserves_other_branches(self):
        engine = create_engine("sqlite:///:memory:")
        self.addCleanup(engine.dispose)

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO offers_raw (id, name) VALUES (1, 'Offer')"))
            parent = "offers_raw"
            # Create a populated FK chain so dropping a parent prematurely fails.
            for table in reversed(RETIRED_AD_STRATEGY_TABLES):
                conn.execute(text(f'CREATE TABLE "{table}" (id INTEGER PRIMARY KEY, parent_id INTEGER REFERENCES "{parent}"(id))'))
                conn.execute(text(f'INSERT INTO "{table}" VALUES (1, 1)'))
                parent = table
        with patch.object(migration, "engine", engine):
            migration.init_db()
            migration.init_db()
        tables = set(inspect(engine).get_table_names())
        self.assertTrue(tables.isdisjoint(RETIRED_AD_STRATEGY_TABLES))
        self.assertTrue({"ugc_creatives", "ad_concepts", "ad_copies", "ad_creative_plans"}.issubset(tables))
        with engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT name FROM offers_raw WHERE id=1")).scalar(), "Offer")
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_key_check").all(), [])

    def test_routes_exclude_retired_branch(self):
        router = APIRouter()
        register_general_routes(router)
        retired = {"ad-strategy", "creative-strategy", "ad-setup", "creative-execution-setups", "generate-ad", "generate-ads", "creative-types"}
        self.assertFalse(any(retired.intersection(route.path.split("/")) for route in router.routes))

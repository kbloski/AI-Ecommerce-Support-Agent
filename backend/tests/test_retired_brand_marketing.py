import unittest

from fastapi import APIRouter
from sqlalchemy import create_engine, event, inspect, text

from api.routes.general_routes import register_general_routes
from domain.models import models
from infrastructure.database.db import Base
from infrastructure.database.retired_brand_marketing_migration import (
    RETIRED_TABLES, remove_retired_brand_marketing_pipeline,
)


class RetiredBrandMarketingTests(unittest.TestCase):
    def test_removes_strategy_tables_and_preserves_profile_resources(self):
        engine = create_engine("sqlite:///:memory:")
        self.addCleanup(engine.dispose)

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO offers_raw (id, name) VALUES (1, 'Offer')"))
            conn.execute(text("INSERT INTO offer_sources (id, offer_id) VALUES (1, 1)"))
            conn.execute(text("INSERT INTO offer_profiles (id, offer_source_id, name) VALUES (1, 1, 'Profile')"))
            conn.execute(text("INSERT INTO page_blueprint (id, offer_profile_id, name, description, is_favorite) VALUES (1, 1, 'Blueprint', '', 0)"))
            parents = ("offer_sources",) + tuple(reversed(RETIRED_TABLES))[:-1]
            for table, parent in zip(reversed(RETIRED_TABLES), parents):
                conn.execute(text(f'CREATE TABLE "{table}" (id INTEGER PRIMARY KEY, parent_id INTEGER REFERENCES "{parent}"(id))'))
                conn.execute(text(f'INSERT INTO "{table}" VALUES (1, 1)'))

        remove_retired_brand_marketing_pipeline(engine)
        remove_retired_brand_marketing_pipeline(engine)
        tables = set(inspect(engine).get_table_names())
        self.assertFalse(tables.intersection(RETIRED_TABLES))
        with engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT name FROM page_blueprint WHERE id=1")).scalar(), "Blueprint")
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_key_check").all(), [])
            self.assertEqual(conn.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)

    def test_external_foreign_key_prevents_removal(self):
        engine = create_engine("sqlite:///:memory:")
        self.addCleanup(engine.dispose)
        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE brand_marketing (id INTEGER PRIMARY KEY)"))
            conn.execute(text("CREATE TABLE external_data (brand_id INTEGER REFERENCES brand_marketing(id))"))
        with self.assertRaisesRegex(RuntimeError, "external_data"):
            remove_retired_brand_marketing_pipeline(engine)
        self.assertIn("brand_marketing", inspect(engine).get_table_names())

    def test_api_has_no_legacy_strategy_routes(self):
        router = APIRouter()
        register_general_routes(router)
        retired = ("brand-marketing", "marketing-strategy", "offer-strategy", "message-strategy", "page-strategy")
        self.assertFalse(any(any(part in route.path for part in retired) for route in router.routes))

import unittest
from unittest.mock import patch

from fastapi import APIRouter
from sqlalchemy import create_engine, inspect, text

from api.routes.general_routes import register_general_routes
from application.dtos.offer_sources.offer_source_dto import OfferSourceDto
from domain.models import models
from infrastructure.database.db import Base
from infrastructure.database import init_db as migration


class RetiredOfferElementsTests(unittest.TestCase):
    def test_retired_storage_is_removed_without_affecting_offer_data(self):
        engine = create_engine("sqlite:///:memory:")
        self.addCleanup(engine.dispose)
        Base.metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO offers_raw (id, name) VALUES (1, 'Offer')"))
            conn.execute(text("INSERT INTO offer_sources (id, offer_id, offer_details) VALUES (1, 1, 'Details')"))
            conn.execute(text("INSERT INTO offer_facts (offer_source_id, name, description) VALUES (1, 'Fact', 'Existing fact')"))
            for table in ("offer_source_elements", "offer_profile_elements"):
                conn.execute(text(f'CREATE TABLE "{table}" (id INTEGER PRIMARY KEY, offer_source_id INTEGER REFERENCES offer_sources(id))'))
                conn.execute(text(f'INSERT INTO "{table}" VALUES (1, 1)'))
        with patch.object(migration, "engine", engine):
            migration.init_db()
            migration.init_db()
        tables = inspect(engine).get_table_names()
        self.assertNotIn("offer_source_elements", tables)
        self.assertNotIn("offer_profile_elements", tables)
        with engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT offer_details FROM offer_sources WHERE id=1")).scalar(), "Details")
            self.assertEqual(conn.execute(text("SELECT COUNT(*) FROM offer_facts")).scalar(), 1)

    def test_offer_source_contract_and_routes_exclude_elements(self):
        dto = OfferSourceDto(1, 1, "Details")
        self.assertEqual(set(dto.to_dict()), {"id", "offer_id", "offer_details", "offer_facts"})
        self.assertEqual(set(dto.to_content_dict()), {"offer_details", "offer_facts"})
        router = APIRouter()
        register_general_routes(router)
        self.assertFalse(any("/offer-source-elements" in route.path or
                             ("/offer-sources/" in route.path and "/elements" in route.path)
                             for route in router.routes))

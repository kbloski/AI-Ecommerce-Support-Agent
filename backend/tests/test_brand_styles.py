import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fastapi import HTTPException

from api.routes.brand_styles_routes import router
from application.services.llm_context_composer import LlmContextComposer
from application.services.resource_context_service import compose_resource_context
from domain.enums.context_type import ContextType
from domain.models import models
from domain.models.brand.brand_style import BrandStyle
from domain.models.offer.offer_profile import OfferProfile
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource
from infrastructure.database.db import Base
from infrastructure.repositories.brand_styles_repository import BrandStylesRepository
from infrastructure.repositories.color_philosophy_repository import ColorPhilosophyRepository
from infrastructure.repositories.typography_philosophy_repository import TypographyPhilosophyRepository
from infrastructure.services.path_service import PathService
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository


class BrandStylesTests(unittest.TestCase):
    FIELDS = {"font_family": "Inter", "brand_color": "#1A73E8", "text_color": "#123456", "background_color": "#ffffff"}

    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})

        @event.listens_for(self.engine, "connect")
        def enable_fk(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add(OfferRaw(id=1, name="Product")); self.db.flush()
        self.db.add(OfferSource(id=1, offer_id=1)); self.db.flush()
        self.db.add_all([OfferProfile(id=1, offer_source_id=1, name="A"), OfferProfile(id=2, offer_source_id=1, name="B")]); self.db.commit()
        self.repo = BrandStylesRepository(None, self.db)
        self.messages = []
        self.compose_calls = []
        self.response = {"font_family": "Lora, serif", "brand_color": "#7A1F2B", "text_color": "#24201E", "background_color": "#faf7f2", "reasoning": "ignored"}
        def chat_json(messages, **kwargs):
            self.messages.extend(messages)
            return self.response
        def compose(root, include=None):
            self.compose_calls.append((root, include))
            return "<offer_profile>Premium tea for gifting</offer_profile>"
        container = SimpleNamespace(
            brand_styles_repository=lambda: self.repo,
            offer_profiles_repository=lambda: OfferProfilesRepository(None, self.db),
            llm_context_composer=lambda: SimpleNamespace(compose=compose),
            color_philosophy_repository=lambda: ColorPhilosophyRepository(None, PathService(None)),
            typography_philosophy_repository=lambda: TypographyPhilosophyRepository(None, PathService(None)),
            ai_service=lambda: SimpleNamespace(chat_json=chat_json),
        )
        self.patchers = [patch(f"application.handlers.brand_styles.{name}.Container", lambda: container)
                         for name in ("brand_style_handlers", "generate_brand_style_handler")]
        for patcher in self.patchers:
            patcher.start()
        app = FastAPI(); app.include_router(router); self.client = TestClient(app)

    def tearDown(self):
        self.client.close(); self.db.close(); self.engine.dispose()
        for patcher in self.patchers:
            patcher.stop()

    def test_generate_saves_style_from_profile_and_source_data(self):
        response = self.client.post("/offer-profiles/1/brand-styles/generate", json={"generation_instructions": "  Elegant, warm  "})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual((response.json()["font_family"], response.json()["background_color"]), ("Lora, serif", "#FAF7F2"))
        self.assertEqual(response.json()["text_color"], "#24201E")
        self.assertEqual(self.db.query(BrandStyle).filter_by(offer_profile_id=1).count(), 1)
        root, include = self.compose_calls[0]
        self.assertEqual((root.type.value, root.id), ("offer_profile", 1))
        self.assertEqual([selection.type.value for selection in include], ["offer_source"])
        self.assertNotIn("offer_source", self.messages[0].content)
        self.assertNotIn("offer_profile", self.messages[0].content)
        self.assertIn("Premium tea for gifting", self.messages[1].content)
        self.assertIn("<color_philosophy", self.messages[1].content)
        self.assertIn("forest green", self.messages[1].content)
        self.assertIn("color philosophy", self.messages[0].content)
        self.assertIn('<typography_philosophy purpose="', self.messages[1].content)
        self.assertIn("humanist sans-serif", self.messages[1].content)
        self.assertIn("typography philosophy", self.messages[0].content)
        self.assertIn('<generation_instructions purpose="', self.messages[1].content)
        self.assertIn(">\nElegant, warm\n</generation_instructions>", self.messages[1].content)
        self.assertIn('<color_philosophy purpose="', self.messages[1].content)

    def test_generate_reasons_first_and_avoids_existing_styles(self):
        self.response = {"offer_category": "tea", "brand_traits": ["warm"], "shade": "burgundy", **self.response}
        self.client.post("/offer-profiles/1/brand-styles", json=self.FIELDS)
        self.client.post("/offer-profiles/2/brand-styles", json={**self.FIELDS, "font_family": "Other profile"})
        response = self.client.post("/offer-profiles/1/brand-styles/generate", json={})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertNotIn("offer_category", response.json())
        self.assertIn("offer_category", self.messages[0].content)
        self.assertIn("brand_traits", self.messages[0].content)
        self.assertIn('<existing_brand_styles purpose="', self.messages[1].content)
        self.assertIn('"font_family": "Inter"', self.messages[1].content)
        self.assertNotIn("Other profile", self.messages[1].content)

    def test_design_references_are_industry_independent(self):
        self.client.post("/offer-profiles/1/brand-styles/generate", json={})
        self.assertNotIn("suitable_for", self.messages[1].content)
        self.assertNotIn("<existing_brand_styles", self.messages[1].content)

    def test_selected_styles_can_be_exported_in_resource_context(self):
        own = self.client.post("/offer-profiles/1/brand-styles", json=self.FIELDS).json()
        self.client.post("/offer-profiles/1/brand-styles", json={**self.FIELDS, "font_family": "Not selected"})
        foreign = self.client.post("/offer-profiles/2/brand-styles", json=self.FIELDS).json()
        composer = LlmContextComposer(
            SimpleNamespace(build_llm_context=lambda id, **kwargs: "<offer_profile>A</offer_profile>"),
            None, None, None, None, brand_styles_repository=self.repo,
        )
        container = SimpleNamespace(llm_context_composer=lambda: composer)
        text = compose_resource_context(container, ContextType.OFFER_PROFILE, 1, [ContextType.BRAND_STYLE], [], order_by_path=True, brand_style_ids=[own["id"]])
        self.assertIn("<brand_styles>", text)
        self.assertIn('"brand_color": "#1A73E8"', text)
        self.assertIn('"text_color": "#123456"', text)
        self.assertNotIn("Not selected", text)
        self.assertLess(text.index("<offer_profile>"), text.index("<brand_styles>"))
        with self.assertRaises(HTTPException) as error:
            compose_resource_context(container, ContextType.OFFER_PROFILE, 1, [ContextType.BRAND_STYLE], [], brand_style_ids=[foreign["id"]])
        self.assertEqual(error.exception.status_code, 422)

    def test_generate_rejects_invalid_ai_output(self):
        self.response = {"font_family": "Inter", "background_color": "white", "brand_color": "#000000", "text_color": "#111111"}
        self.assertEqual(self.client.post("/offer-profiles/1/brand-styles/generate", json={}).status_code, 502)
        self.assertNotIn("<generation_instructions", self.messages[1].content)
        self.assertEqual(self.client.post("/offer-profiles/999/brand-styles/generate", json={}).status_code, 404)
        self.assertEqual(self.db.query(BrandStyle).count(), 0)

    def test_create_list_update_and_delete(self):
        created = self.client.post("/offer-profiles/1/brand-styles", json={**self.FIELDS, "font_family": "  Inter  "})
        self.assertEqual(created.status_code, 201, created.text)
        style = created.json()
        self.assertEqual((style["font_family"], style["brand_color"], style["text_color"], style["background_color"]), ("Inter", "#1A73E8", "#123456", "#FFFFFF"))
        self.assertEqual([item["id"] for item in self.client.get("/offer-profiles/1/brand-styles").json()], [style["id"]])
        self.assertEqual(self.client.get("/offer-profiles/2/brand-styles").json(), [])
        updated = self.client.post(f"/brand-styles/{style['id']}/update", json={**self.FIELDS, "font_family": "Roboto"})
        self.assertEqual(updated.json()["font_family"], "Roboto")
        self.assertEqual(self.client.delete(f"/brand-styles/{style['id']}/delete").status_code, 200)
        self.assertEqual(self.db.query(BrandStyle).count(), 0)

    def test_validation_and_missing_entities(self):
        for payload in ({**self.FIELDS, "font_family": " "}, {**self.FIELDS, "brand_color": "blue"},
                        {**self.FIELDS, "text_color": "#FFF"}, {**self.FIELDS, "background_color": "#FFF"},
                        {**self.FIELDS, "extra": 1}):
            self.assertEqual(self.client.post("/offer-profiles/1/brand-styles", json=payload).status_code, 422)
        self.assertEqual(self.client.post("/offer-profiles/999/brand-styles", json=self.FIELDS).status_code, 404)
        self.assertEqual(self.client.get("/offer-profiles/999/brand-styles").status_code, 404)
        self.assertEqual(self.client.post("/brand-styles/999/update", json=self.FIELDS).status_code, 404)
        self.assertEqual(self.client.delete("/brand-styles/999/delete").status_code, 404)

    def test_styles_are_deleted_with_their_profile(self):
        self.client.post("/offer-profiles/1/brand-styles", json=self.FIELDS)
        self.db.execute(text("DELETE FROM offer_profiles WHERE id=1")); self.db.commit()
        self.assertEqual(self.db.query(BrandStyle).count(), 0)

    def test_legacy_styles_gain_text_color_without_losing_colors(self):
        from infrastructure.database import init_db as migration

        legacy = create_engine("sqlite://")
        try:
            with legacy.begin() as conn:
                conn.execute(text(
                    "CREATE TABLE brand_styles (id INTEGER PRIMARY KEY, font_family VARCHAR(255), "
                    "brand_color VARCHAR(7), background_color VARCHAR(7))"
                ))
                conn.execute(text(
                    "INSERT INTO brand_styles (id, font_family, brand_color, background_color) "
                    "VALUES (1, 'Inter', '#123456', '#FFFFFF')"
                ))
            with patch.object(migration, "engine", legacy):
                migration._add_brand_style_text_color()
                migration._add_brand_style_text_color()
            with legacy.connect() as conn:
                self.assertIn("text_color", {column["name"] for column in inspect(conn).get_columns("brand_styles")})
                self.assertEqual(conn.execute(text(
                    "SELECT brand_color, text_color, background_color FROM brand_styles WHERE id=1"
                )).one(), ("#123456", "#000000", "#FFFFFF"))
        finally:
            legacy.dispose()


if __name__ == "__main__":
    unittest.main()

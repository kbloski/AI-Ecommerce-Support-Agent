import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes.resource_context_routes import router
from application.services.llm_context_composer import ContextRef, ContextSelection, LlmContextComposer
from application.services.offer_profile_service import OfferProfileService
from application.services.ad_concept_service import AdConceptService
from domain.enums.context_type import ContextType


class ResourceContextTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.fact_selections = []
        self.additional_context_selections = []
        self.path_order_selections = []

        def compose(*, root, include, include_offer_facts=True, include_additional_contexts=True, order_by_path=False):
            self.calls.append((root, include))
            self.fact_selections.append(include_offer_facts)
            self.additional_context_selections.append(include_additional_contexts)
            self.path_order_selections.append(order_by_path)
            if root.id == 999:
                raise LookupError("Resource not found")
            return f"<{root.type.value}>\nDane źródła\n</{root.type.value}>"

        container = SimpleNamespace(
            llm_context_composer=lambda: SimpleNamespace(compose=compose),
            offer_source_repository=lambda: SimpleNamespace(get_by_id=lambda id: object() if id != 999 else None),
        )
        self.patcher = patch("api.routes.resource_context_routes.Container", lambda: container)
        self.patcher.start()
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.patcher.stop()

    def test_downloads_each_resource_as_utf8_attachment(self):
        for resource_type in ("offer_raw", "offer_source", "offer_profile"):
            with self.subTest(resource_type=resource_type):
                response = self.client.get(f"/resources/{resource_type}/1/context/download")
                self.assertEqual(response.status_code, 200, response.text)
                self.assertTrue(response.headers["content-type"].startswith("text/plain"))
                self.assertEqual(response.headers["content-disposition"], f'attachment; filename="{resource_type}_1_context.txt"')
                self.assertIn("Dane źródła", response.content.decode("utf-8"))
                self.assertEqual(self.calls[-1], (ContextRef(ContextType(resource_type), 1), []))
                self.assertTrue(self.path_order_selections[-1])

    def test_profile_include_is_passed_to_composer(self):
        response = self.client.get("/resources/offer_profile/3/context", params=[
            ("include", "offer_source"), ("include", "offer_raw"), ("include", "target_audiences"),
            ("include", "marketing_angle"), ("marketing_angle_ids", "2"),
        ])
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn("content-disposition", response.headers)
        self.assertEqual(self.calls[-1], (
            ContextRef(ContextType.OFFER_PROFILE, 3),
            [ContextSelection(ContextType.OFFER_SOURCE), ContextSelection(ContextType.OFFER_RAW), ContextSelection(ContextType.TARGET_AUDIENCES),
             ContextSelection(ContextType.MARKETING_ANGLE, include_ids=(2,))],
        ))

    def test_source_can_include_its_raw_offer(self):
        response = self.client.get("/resources/offer_source/3/context", params={"include": "offer_raw"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.calls[-1], (
            ContextRef(ContextType.OFFER_SOURCE, 3), [ContextSelection(ContextType.OFFER_RAW)],
        ))

    def test_profile_can_select_ad_concepts_for_preview_and_download(self):
        for suffix in ("", "/download"):
            response = self.client.get(f"/resources/offer_profile/3/context{suffix}", params=[
                ("include", "ad_concept"), ("ad_concept_ids", "4"), ("ad_concept_ids", "5"),
            ])
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(self.calls[-1][1], [ContextSelection(ContextType.AD_CONCEPT, include_ids=(4, 5))])
        self.assertEqual(self.client.get("/resources/offer_profile/3/context", params={"include": "ad_concept"}).status_code, 422)
        self.assertEqual(self.client.get("/resources/offer_profile/3/context", params={"ad_concept_ids": 4}).status_code, 422)
        self.assertEqual(self.client.get("/resources/offer_source/3/context", params={"include": "ad_concept"}).status_code, 422)

    def test_fact_selection_is_used_for_preview_and_download(self):
        for suffix in ("", "/download"):
            response = self.client.get(
                f"/resources/offer_source/3/context{suffix}",
                params={"include_offer_facts": "false"},
            )
            self.assertEqual(response.status_code, 200, response.text)
            self.assertFalse(self.fact_selections[-1])

    def test_additional_context_selection_is_used_for_preview_and_download(self):
        for suffix in ("", "/download"):
            response = self.client.get(
                f"/resources/offer_profile/3/context{suffix}",
                params={"include_additional_contexts": "false"},
            )
            self.assertEqual(response.status_code, 200, response.text)
            self.assertFalse(self.additional_context_selections[-1])
        self.assertEqual(
            self.client.get("/resources/offer_source/3/context", params={"include_additional_contexts": "false"}).status_code,
            422,
        )

    def test_rejects_invalid_types_selections_and_missing_resource(self):
        self.assertEqual(self.client.get("/resources/offer_raw/1/context", params={"include": "offer_source"}).status_code, 422)
        self.assertEqual(self.client.get("/resources/offer_source/1/context", params={"marketing_angle_ids": 2}).status_code, 422)
        self.assertEqual(self.client.get("/resources/offer_profile/1/context", params={"include": "marketing_angle"}).status_code, 422)
        self.assertEqual(self.client.get("/resources/offer_profile/1/context", params={"include": "offer_profile"}).status_code, 422)
        self.assertEqual(self.client.get("/resources/target_audiences/1/context").status_code, 422)
        self.assertEqual(self.client.get("/resources/offer_source/999/context").status_code, 404)
        self.assertEqual(self.client.get("/resources/offer_raw/999/context").status_code, 404)

    def test_composer_supports_offer_source_root_without_includes(self):
        source_service = SimpleNamespace(
            build_llm_context=lambda id, include_related=True: f"source:{id}" if include_related else f"source-without-facts:{id}",
            get_offer_source_details_by_id=lambda id: SimpleNamespace(offer_id=7),
        )
        raw_service = SimpleNamespace(build_llm_context=lambda id: f"raw:{id}")
        profile_service = SimpleNamespace(
            build_llm_context=lambda id, include_additional_contexts=True: f"profile:{id}" if include_additional_contexts else f"profile-without-contexts:{id}",
            get_offer_profile_details_by_id=lambda id: SimpleNamespace(offer_source_id=4),
        )
        audience_service = SimpleNamespace(build_llm_context=lambda id, include_ids=None, exclude_ids=None: f"audiences:{id}")
        angle_service = SimpleNamespace(build_llm_context=lambda id, ids: f"angles:{id}:{ids}")
        concept_service = SimpleNamespace(build_llm_context=lambda id, ids: f"concepts:{id}:{ids}")
        composer = LlmContextComposer(profile_service, audience_service, raw_service, source_service, angle_service, concept_service)
        self.assertEqual(composer.compose(ContextRef(ContextType.OFFER_SOURCE, 4)), "source:4")
        self.assertEqual(
            composer.compose(ContextRef(ContextType.OFFER_SOURCE, 4), include_offer_facts=False),
            "source-without-facts:4",
        )
        self.assertEqual(
            composer.compose(ContextRef(ContextType.OFFER_SOURCE, 4), [ContextSelection(ContextType.OFFER_RAW)]),
            "source:4\n\nraw:7",
        )
        self.assertEqual(
            composer.compose(ContextRef(ContextType.OFFER_SOURCE, 4), [ContextSelection(ContextType.OFFER_RAW)], order_by_path=True),
            "raw:7\n\nsource:4",
        )
        self.assertEqual(
            composer.compose(ContextRef(ContextType.OFFER_PROFILE, 2), [
                ContextSelection(ContextType.OFFER_SOURCE), ContextSelection(ContextType.OFFER_RAW),
            ]),
            "profile:2\n\nsource:4\n\nraw:7",
        )
        self.assertEqual(
            composer.compose(ContextRef(ContextType.OFFER_PROFILE, 2), [
                ContextSelection(ContextType.OFFER_SOURCE), ContextSelection(ContextType.OFFER_RAW),
            ], order_by_path=True),
            "raw:7\n\nsource:4\n\nprofile:2",
        )
        self.assertEqual(
            composer.compose(ContextRef(ContextType.OFFER_PROFILE, 2), [
                ContextSelection(ContextType.MARKETING_ANGLE, include_ids=(8,)),
                ContextSelection(ContextType.AD_CONCEPT, include_ids=(9,)),
                ContextSelection(ContextType.OFFER_SOURCE),
                ContextSelection(ContextType.TARGET_AUDIENCES),
                ContextSelection(ContextType.OFFER_RAW),
            ], order_by_path=True),
            "raw:7\n\nsource:4\n\nprofile:2\n\naudiences:2\n\nangles:2:[8]\n\nconcepts:2:[9]",
        )
        self.assertEqual(
            composer.compose(ContextRef(ContextType.OFFER_PROFILE, 2), [
                ContextSelection(ContextType.OFFER_SOURCE), ContextSelection(ContextType.OFFER_RAW),
            ], include_offer_facts=False),
            "profile:2\n\nsource-without-facts:4\n\nraw:7",
        )
        self.assertEqual(
            composer.compose(ContextRef(ContextType.OFFER_PROFILE, 2), include_additional_contexts=False),
            "profile-without-contexts:2",
        )
        with self.assertRaises(ValueError):
            composer.compose(ContextRef(ContextType.OFFER_SOURCE, 4), [ContextSelection(ContextType.TARGET_AUDIENCES)])

    def test_profile_service_omits_additional_contexts_when_unselected(self):
        service = OfferProfileService(None, None)
        service.get_offer_profile_details_by_id = lambda id: SimpleNamespace(
            to_content_dict=lambda: {"name": "Profile", "additional_contexts": [{"name": "Notes", "content": "Text"}]},
        )
        self.assertIn('"additional_contexts"', service.build_llm_context(2))
        self.assertNotIn('"additional_contexts"', service.build_llm_context(2, include_additional_contexts=False))

    def test_ad_concept_context_uses_selected_concepts_from_profile(self):
        concept = SimpleNamespace(
            id=4, offer_profile_id=3, name="Idea", description="Description", format="image",
            core_idea="Visual", key_message="Message", generation_mode="standard", marketing_angles=[],
        )
        foreign = SimpleNamespace(**{**vars(concept), "id": 5, "offer_profile_id": 8})
        service = AdConceptService(SimpleNamespace(get_by_id=lambda id: {4: concept, 5: foreign}.get(id)))
        context = service.build_llm_context(3, [4])
        self.assertIn('"core_idea": "Visual"', context)
        self.assertIn('<ad_concepts purpose=', context)
        with self.assertRaises(ValueError):
            service.build_llm_context(3, [4, 5])
        with self.assertRaises(LookupError):
            service.build_llm_context(3, [999])


if __name__ == "__main__":
    unittest.main()

from dataclasses import dataclass
import json

from domain.enums.context_type import ContextType
from application.services.llm_context_builder import build_llm_section
from application.services.offer_profile_service import OfferProfileService
from application.services.offer_service import OfferService
from application.services.offer_source_service import OfferSourceService
from application.services.target_audience_service import TargetAudienceService
from application.services.marketing_angle_service import MarketingAngleService
from application.services.ad_concept_service import AdConceptService
from application.mappers.analysis_mapper import AnalysisMapper
from application.mappers.checklist_mapper import ChecklistMapper


@dataclass(frozen=True)
class ContextRef:
    type: ContextType
    id: int


@dataclass(frozen=True)
class ContextSelection:
    type: ContextType
    include_ids: tuple[int, ...] | None = None
    exclude_ids: tuple[int, ...] = ()


class LlmContextComposer:
    def __init__(
        self,
        offer_profile_service: OfferProfileService,
        target_audience_service: TargetAudienceService,
        offer_service: OfferService,
        offer_source_service: OfferSourceService,
        marketing_angle_service: MarketingAngleService,
        ad_concept_service: AdConceptService | None = None,
        ad_copies_repository=None,
        ad_creative_plans_repository=None,
        ugc_creative_repository=None,
        brand_styles_repository=None,
        analysis_repository=None,
        offer_profile_analysis_repository=None,
        analysis_assembler=None,
        checklist_repository=None,
        checklist_assembler=None,
        page_blueprint_service=None,
        page_service=None,
        notes_repository=None,
    ):
        self.offer_profile_service = offer_profile_service
        self.target_audience_service = target_audience_service
        self.offer_service = offer_service
        self.offer_source_service = offer_source_service
        self.marketing_angle_service = marketing_angle_service
        self.ad_concept_service = ad_concept_service
        self.profile_export_repositories = {
            ContextType.CREATIVE_PLAN: ad_creative_plans_repository,
            ContextType.UGC_CREATIVE: ugc_creative_repository,
            ContextType.AD_COPY: ad_copies_repository,
            ContextType.BRAND_STYLE: brand_styles_repository,
        }
        self.analysis_repository = analysis_repository
        self.offer_profile_analysis_repository = offer_profile_analysis_repository
        self.analysis_assembler = analysis_assembler
        self.checklist_repository = checklist_repository
        self.checklist_assembler = checklist_assembler
        self.page_blueprint_service = page_blueprint_service
        self.page_service = page_service
        self.notes_repository = notes_repository

    def _selected_documents(self, kind: ContextType, profile_id: int | None, ids: tuple[int, ...] | None) -> str:
        if not ids or len(ids) != len(set(ids)):
            raise ValueError(f"Select unique {kind.value} IDs")
        items = []
        for item_id in ids:
            if kind == ContextType.NOTE:
                item = self.notes_repository.get_by_id(item_id)
                if item is None:
                    raise LookupError(f"note {item_id} not found")
                items.append({"title": item.title, "content": item.content})
                continue
            if kind == ContextType.ANALYSIS:
                item = self.analysis_repository.get_by_id(item_id)
                if item is None:
                    raise LookupError(f"analysis {item_id} not found")
                if self.offer_profile_analysis_repository.find_relation(profile_id, item_id) is None:
                    raise ValueError("Selected analysis must belong to this offer profile")
                dto = self.analysis_assembler.assemble_dto(AnalysisMapper.to_dto(item))
                items.append(dto.to_content_dict())
                continue
            if kind == ContextType.CHECKLIST:
                item = self.checklist_repository.get_by_id(item_id)
                if item is None:
                    raise LookupError(f"checklist {item_id} not found")
                if item.offer_profile_id != profile_id:
                    raise ValueError("Selected checklist must belong to this offer profile")
                dto = self.checklist_assembler.assemble_dto(ChecklistMapper.to_dto(item))
                items.append(dto.to_content_dict())
                continue
            if kind == ContextType.PAGE_BLUEPRINT:
                dto = self.page_blueprint_service.get_page_blueprint_by_id(item_id)
                if dto.offer_profile_id != profile_id:
                    raise ValueError("Selected page blueprint must belong to this offer profile")
                items.append(dto.to_content_dict())
                continue
            if kind == ContextType.PAGE:
                page = self.page_service.get_by_id(item_id)
                if page["offer_profile_id"] != profile_id:
                    raise ValueError("Selected page must belong to this offer profile")
                items.append({key: ([{field: value for field, value in section.items() if field != "id"}
                                      for section in page["sections"]] if key == "sections" else value)
                              for key, value in page.items() if key not in {"id", "offer_profile_id", "is_favorite"}})
        tag = {ContextType.ANALYSIS: "analyses", ContextType.CHECKLIST: "checklists",
               ContextType.PAGE_BLUEPRINT: "page_blueprints", ContextType.PAGE: "pages",
               ContextType.NOTE: "notes"}[kind]
        return build_llm_section(tag, json.dumps(items, ensure_ascii=False, indent=2))

    def _selected_profile_items(self, kind: ContextType, profile_id: int, ids: tuple[int, ...] | None) -> str:
        if not ids or len(ids) != len(set(ids)):
            raise ValueError(f"Select unique {kind.value} IDs")
        repository = self.profile_export_repositories[kind]
        if repository is None:
            raise ValueError(f"{kind.value} context is unavailable")
        fields = {
            ContextType.CREATIVE_PLAN: ("id", "name", "description", "format", "plan", "ad_concept_id", "is_reviewed"),
            ContextType.UGC_CREATIVE: ("id", "name", "customer_persona", "content_format", "angle", "hook_idea", "video_flow", "recording_style", "platform_fit", "cta", "why_it_should_work", "is_reviewed"),
            ContextType.AD_COPY: ("id", "name", "primary_text", "headline", "description", "cta", "is_reviewed"),
            ContextType.BRAND_STYLE: ("id", "font_family", "brand_color", "text_color", "background_color"),
        }[kind]
        items = []
        for item_id in ids:
            item = repository.get_by_id(item_id)
            if item is None:
                raise LookupError(f"{kind.value} {item_id} not found")
            if item.offer_profile_id != profile_id:
                raise ValueError(f"Selected {kind.value} must belong to this offer profile")
            items.append({field: getattr(item, field) for field in fields})
        tag = {
            ContextType.CREATIVE_PLAN: "creative_plans",
            ContextType.UGC_CREATIVE: "ugc_creatives",
            ContextType.AD_COPY: "ad_copies",
            ContextType.BRAND_STYLE: "brand_styles",
        }[kind]
        return build_llm_section(tag, json.dumps(items, ensure_ascii=False, indent=2))

    def compose(
        self,
        root: ContextRef,
        include: list[ContextSelection] | None = None,
        *,
        include_offer_facts: bool = True,
        include_additional_contexts: bool = True,
        order_by_path: bool = False,
    ) -> str:
        def source_context(source_id: int) -> str:
            if include_offer_facts:
                return self.offer_source_service.build_llm_context(source_id)
            return self.offer_source_service.build_llm_context(source_id, include_related=False)

        if root.type == ContextType.OFFER_RAW:
            sections = [self.offer_service.build_llm_context(root.id)]
            for selection in include or []:
                if selection.type != ContextType.NOTE or selection.exclude_ids:
                    raise ValueError("Offer raw context only supports notes")
                sections.append(self._selected_documents(ContextType.NOTE, None, selection.include_ids))
            return "\n\n".join(sections)
        if root.type == ContextType.OFFER_SOURCE:
            sections = [(ContextType.OFFER_SOURCE, source_context(root.id))]
            for selection in include or []:
                if selection.type == ContextType.NOTE and not selection.exclude_ids:
                    sections.append((ContextType.NOTE, self._selected_documents(ContextType.NOTE, None, selection.include_ids)))
                elif selection.type == ContextType.OFFER_RAW and selection.include_ids is None and not selection.exclude_ids:
                    source = self.offer_source_service.get_offer_source_details_by_id(root.id)
                    sections.append((ContextType.OFFER_RAW, self.offer_service.build_llm_context(source.offer_id)))
                else:
                    raise ValueError("Offer source context only supports its raw offer and notes")
            if len({selection.type for selection in include or []}) != len(include or []):
                raise ValueError("Duplicate offer raw selection")
            if order_by_path:
                sections.sort(key=lambda item: {ContextType.OFFER_RAW: 0, ContextType.OFFER_SOURCE: 1, ContextType.NOTE: 2}[item[0]])
            return "\n\n".join(content for _, content in sections)
        if root.type != ContextType.OFFER_PROFILE:
            raise ValueError(f"Unsupported context root: {root.type}")

        if include_additional_contexts:
            profile_context = self.offer_profile_service.build_llm_context(root.id)
        else:
            profile_context = self.offer_profile_service.build_llm_context(root.id, include_additional_contexts=False)
        sections = [(ContextType.OFFER_PROFILE, profile_context)]
        seen = set()
        for selection in include or []:
            if selection.type in seen:
                raise ValueError(f"Duplicate context selection: {selection.type}")
            seen.add(selection.type)
            if selection.type == ContextType.OFFER_SOURCE:
                if selection.include_ids is not None or selection.exclude_ids:
                    raise ValueError("Offer source selection does not support ID filters")
                profile = self.offer_profile_service.get_offer_profile_details_by_id(root.id)
                sections.append((ContextType.OFFER_SOURCE, source_context(profile.offer_source_id)))
                continue
            if selection.type == ContextType.OFFER_RAW:
                if selection.include_ids is not None or selection.exclude_ids:
                    raise ValueError("Offer raw selection does not support ID filters")
                profile = self.offer_profile_service.get_offer_profile_details_by_id(root.id)
                source = self.offer_source_service.get_offer_source_details_by_id(profile.offer_source_id)
                sections.append((ContextType.OFFER_RAW, self.offer_service.build_llm_context(source.offer_id)))
                continue
            if selection.type == ContextType.MARKETING_ANGLE:
                if not selection.include_ids or selection.exclude_ids:
                    raise ValueError("Select at least one marketing angle without exclusions")
                sections.append((ContextType.MARKETING_ANGLE, self.marketing_angle_service.build_llm_context(root.id, list(selection.include_ids))))
                continue
            if selection.type == ContextType.AD_CONCEPT:
                if not selection.include_ids or selection.exclude_ids:
                    raise ValueError("Select at least one ad concept without exclusions")
                if self.ad_concept_service is None:
                    raise ValueError("Ad concept context is unavailable")
                sections.append((ContextType.AD_CONCEPT, self.ad_concept_service.build_llm_context(root.id, list(selection.include_ids))))
                continue
            if selection.type in self.profile_export_repositories:
                if selection.exclude_ids:
                    raise ValueError(f"{selection.type.value} does not support exclusions")
                sections.append((selection.type, self._selected_profile_items(selection.type, root.id, selection.include_ids)))
                continue
            if selection.type in (ContextType.ANALYSIS, ContextType.CHECKLIST, ContextType.PAGE_BLUEPRINT, ContextType.PAGE, ContextType.NOTE):
                if selection.exclude_ids:
                    raise ValueError(f"{selection.type.value} does not support exclusions")
                sections.append((selection.type, self._selected_documents(selection.type, root.id, selection.include_ids)))
                continue
            if selection.type != ContextType.TARGET_AUDIENCES:
                raise ValueError(f"Unsupported context selection: {selection.type}")
            try:
                section = self.target_audience_service.build_llm_context(
                    root.id,
                    include_ids=None if selection.include_ids is None else list(selection.include_ids),
                    exclude_ids=list(selection.exclude_ids),
                )
            except LookupError as error:
                raise ValueError(str(error)) from error
            if section:
                sections.append((ContextType.TARGET_AUDIENCES, section))

        if order_by_path:
            order = {
                ContextType.OFFER_RAW: 0,
                ContextType.OFFER_SOURCE: 1,
                ContextType.OFFER_PROFILE: 2,
                ContextType.TARGET_AUDIENCES: 3,
                ContextType.MARKETING_ANGLE: 4,
                ContextType.AD_CONCEPT: 5,
                ContextType.CREATIVE_PLAN: 6,
                ContextType.UGC_CREATIVE: 7,
                ContextType.AD_COPY: 8,
                ContextType.BRAND_STYLE: 9,
                ContextType.ANALYSIS: 10,
                ContextType.CHECKLIST: 11,
                ContextType.PAGE_BLUEPRINT: 12,
                ContextType.PAGE: 13,
                ContextType.NOTE: 14,
            }
            sections.sort(key=lambda item: order[item[0]])
        return "\n\n".join(content for _, content in sections)

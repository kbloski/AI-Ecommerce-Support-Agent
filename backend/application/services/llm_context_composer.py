from dataclasses import dataclass

from domain.enums.context_type import ContextType
from application.services.offer_profile_service import OfferProfileService
from application.services.offer_service import OfferService
from application.services.offer_source_service import OfferSourceService
from application.services.target_audience_service import TargetAudienceService
from application.services.marketing_angle_service import MarketingAngleService
from application.services.ad_concept_service import AdConceptService


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
    ):
        self.offer_profile_service = offer_profile_service
        self.target_audience_service = target_audience_service
        self.offer_service = offer_service
        self.offer_source_service = offer_source_service
        self.marketing_angle_service = marketing_angle_service
        self.ad_concept_service = ad_concept_service

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
            if include:
                raise ValueError("Offer raw context does not support related selections")
            return self.offer_service.build_llm_context(root.id)
        if root.type == ContextType.OFFER_SOURCE:
            sections = [source_context(root.id)]
            for selection in include or []:
                if selection.type != ContextType.OFFER_RAW or selection.include_ids is not None or selection.exclude_ids:
                    raise ValueError("Offer source context only supports its raw offer without ID filters")
                source = self.offer_source_service.get_offer_source_details_by_id(root.id)
                sections.append(self.offer_service.build_llm_context(source.offer_id))
            if len(include or []) > 1:
                raise ValueError("Duplicate offer raw selection")
            if order_by_path:
                sections.reverse()
            return "\n\n".join(sections)
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
            }
            sections.sort(key=lambda item: order[item[0]])
        return "\n\n".join(content for _, content in sections)

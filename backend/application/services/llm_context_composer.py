from dataclasses import dataclass

from domain.enums.context_type import ContextType
from application.services.offer_profile_service import OfferProfileService
from application.services.offer_service import OfferService
from application.services.offer_source_service import OfferSourceService
from application.services.target_audience_service import TargetAudienceService
from application.services.marketing_angle_service import MarketingAngleService


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
    ):
        self.offer_profile_service = offer_profile_service
        self.target_audience_service = target_audience_service
        self.offer_service = offer_service
        self.offer_source_service = offer_source_service
        self.marketing_angle_service = marketing_angle_service

    def compose(self, root: ContextRef, include: list[ContextSelection] | None = None) -> str:
        if root.type == ContextType.OFFER_RAW:
            if include:
                raise ValueError("Offer raw context does not support related selections")
            return self.offer_service.build_llm_context(root.id)
        if root.type != ContextType.OFFER_PROFILE:
            raise ValueError(f"Unsupported context root: {root.type}")

        sections = [self.offer_profile_service.build_llm_context(root.id)]
        seen = set()
        for selection in include or []:
            if selection.type in seen:
                raise ValueError(f"Duplicate context selection: {selection.type}")
            seen.add(selection.type)
            if selection.type == ContextType.OFFER_SOURCE:
                if selection.include_ids is not None or selection.exclude_ids:
                    raise ValueError("Offer source selection does not support ID filters")
                profile = self.offer_profile_service.get_offer_profile_details_by_id(root.id)
                sections.append(self.offer_source_service.build_llm_context(profile.offer_source_id))
                continue
            if selection.type == ContextType.MARKETING_ANGLE:
                if selection.include_ids is None or len(selection.include_ids) != 1 or selection.exclude_ids:
                    raise ValueError("Select exactly one marketing angle")
                sections.append(self.marketing_angle_service.build_llm_context(root.id, selection.include_ids[0]))
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
                sections.append(section)

        return "\n\n".join(sections)

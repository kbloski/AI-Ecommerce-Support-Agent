import json

from application.mappers.target_audience_mapper import TargetAudienceMapper
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose
from infrastructure.repositories.target_audiences_repository import TargetAudiencesRepository
from application.dtos.audience.target_audience_dto import TargetAudienceDto

class TargetAudienceService:
    def __init__(self, target_audiences_repository: TargetAudiencesRepository):
        self.target_audiences_repository = target_audiences_repository

    def get_target_audience_details_by_id(self, target_audience_id: int) -> TargetAudienceDto:
        audience = self.target_audiences_repository.find_by_id(target_audience_id)
        if audience is None:
            raise LookupError(f"Target audience {target_audience_id} not found")
        return TargetAudienceMapper.to_dto(audience)

    def build_llm_context(
        self,
        offer_profile_id: int,
        include_ids: list[int] | None = None,
        exclude_ids: list[int] | None = None,
    ) -> str | None:
        exclude_ids = exclude_ids or []
        if include_ids is not None and len(set(include_ids)) != len(include_ids):
            raise ValueError("Included target audiences must be unique")
        if len(set(exclude_ids)) != len(exclude_ids):
            raise ValueError("Excluded target audiences must be unique")

        if include_ids is None:
            audiences = [
                TargetAudienceMapper.to_dto(item)
                for item in self.target_audiences_repository.find_for_offer_profile(offer_profile_id)
            ]
        else:
            audiences = [self.get_target_audience_details_by_id(id) for id in include_ids]

        exclusions = [self.get_target_audience_details_by_id(id) for id in exclude_ids]
        if any(audience.offer_profile_id != offer_profile_id for audience in audiences + exclusions):
            raise ValueError("Selected target audiences must belong to this offer profile")
        excluded = set(exclude_ids)
        audiences = [audience for audience in audiences if audience.id not in excluded]
        if not audiences:
            return None
        content = json.dumps(
            [audience.to_content_dict() for audience in audiences],
            ensure_ascii=False,
            indent=2,
        )
        return build_llm_section(
            "target_audiences", content,
            purpose=ContextSectionPurpose.TARGET_AUDIENCES.value,
        )

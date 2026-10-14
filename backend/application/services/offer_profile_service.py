import json
from application.mappers.offer_profile_mapper import OfferProfileMapper
from application.services.llm_context_builder import build_llm_section
from application.dtos.offer_profiles.offer_profile_dto import OfferProfileDto
from domain.enums.context_section_purpose import ContextSectionPurpose


class OfferProfileService:
    def __init__(self, offer_profiles_repository, offer_profile_assembler):
        self.offer_profiles_repository = offer_profiles_repository
        self.offer_profile_assembler = offer_profile_assembler

    def get_offer_profile_details_by_id(self, offer_profile_id: int) -> OfferProfileDto:
        profile = self.offer_profiles_repository.get_by_id(offer_profile_id)
        if profile is None:
            raise LookupError(f"Offer profile {offer_profile_id} not found")
        return self.offer_profile_assembler.assemble_dto(OfferProfileMapper.to_dto(profile))

    def build_llm_context(self, offer_profile_id: int) -> str:
        content = json.dumps(
            self.get_offer_profile_details_by_id(offer_profile_id).to_content_dict(),
            ensure_ascii=False, indent=2, default=str,
        )
        return build_llm_section("offer_profile", content, purpose=ContextSectionPurpose.OFFER_PROFILE.value)

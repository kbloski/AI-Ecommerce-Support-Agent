from domain.models.offer_profiles.offer_profile import OfferProfile
from application.dtos.offer_profiles.offer_profile_dto import OfferProfileDto

class OfferProfileMapper:

    @staticmethod
    def to_dto(item : OfferProfile) -> OfferProfileDto:
        return OfferProfileDto(
            id = item.id,
            offer_id = item.offer_id,
            offer_summary = item.offer_summary,
            category = item.category,
            value_proposition = item.value_proposition,
        )

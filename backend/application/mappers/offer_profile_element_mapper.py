from application.dtos.offer_profiles.offer_profile_element_dto import OfferProfileElementDto
from domain.models.offer_profiles.offer_profile_element import OfferProfileElement


class OfferProfileElementMapper:
    @staticmethod
    def to_dto(item: OfferProfileElement) -> OfferProfileElementDto:
        return OfferProfileElementDto(
            id=item.id,
            offer_profile_id=item.offer_profile_id,
            type=item.type.value,
            name=item.name,
            description=item.description,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

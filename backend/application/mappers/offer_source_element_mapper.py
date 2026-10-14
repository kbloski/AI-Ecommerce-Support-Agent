from application.dtos.offer_sources.offer_source_element_dto import OfferSourceElementDto
from domain.models.offer.offer_source_element import OfferSourceElement


class OfferSourceElementMapper:
    @staticmethod
    def to_dto(item: OfferSourceElement) -> OfferSourceElementDto:
        return OfferSourceElementDto(
            id=item.id,
            offer_source_id=item.offer_source_id,
            type=item.type.value,
            name=item.name,
            description=item.description,
            is_reviewed=item.is_reviewed,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

from domain.models.offer.offer_source import OfferSource
from application.dtos.offer_sources.offer_source_dto import OfferSourceDto

class OfferSourceMapper:

    @staticmethod
    def to_dto(item : OfferSource) -> OfferSourceDto:
        return OfferSourceDto(
            id = item.id,
            offer_id = item.offer_id,
            offer_summary = item.offer_summary,
            category = item.category,
            value_proposition = item.value_proposition,
        )

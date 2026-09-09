from domain.models.offers.offer_raw import OfferRaw
from application.dtos.offers.offer_dto import OfferDto

class OfferMapper:

    @staticmethod
    def to_dto(item: OfferRaw) -> OfferDto:
        return OfferDto(
            id = item.id,
            name=item.name,
            description=item.description,
        )


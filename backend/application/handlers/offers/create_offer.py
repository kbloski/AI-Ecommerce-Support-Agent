from di.container import Container
from domain.models.offers.offer_raw import OfferRaw
from application.mappers.offer_mapper import OfferMapper


def create_offer(
    name: str,
    description: str | None = None,
):
    container = Container()
    offers_repository = container.offers_repository()

    offer = OfferRaw(
        name=name,
        description=description,
    )

    created_offer = offers_repository.create(offer)

    return OfferMapper.to_dto(item=created_offer)

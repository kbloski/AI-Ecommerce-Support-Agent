from di.container import Container
from application.mappers.offer_source_mapper import OfferSourceMapper


# =====================================================
# MAIN HANDLER
# =====================================================

def get_offer_sources_handler(
    offer_id: int,
):
    container = Container()

    offer_source_repository = (
        container.offer_source_repository()
    )


    items = offer_source_repository.get_by_offer_id(
        offer_id
    )

    dtos = [
        OfferSourceMapper.to_dto(item)
        for item in items
    ]

    return dtos

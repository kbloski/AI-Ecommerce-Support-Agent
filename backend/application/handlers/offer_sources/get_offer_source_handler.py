from di.container import Container
from application.mappers.offer_source_mapper import OfferSourceMapper


# =====================================================
# MAIN HANDLER
# =====================================================

def get_offer_source_handler(
    offer_source_id: int
):
    container = Container()

    offer_source_repository = (
        container.offer_source_repository()
    )

    offer_source_assembler = (
        container.offer_source_assembler()
    )


    item = offer_source_repository.get_by_id(
        offer_source_id
    )

    if not item:
        raise ValueError(
            f"OfferSource {offer_source_id} not found"
        )


    item_dto = OfferSourceMapper.to_dto(
        item
    )


    result = offer_source_assembler.assemble_dto(
        item_dto
    )


    return result

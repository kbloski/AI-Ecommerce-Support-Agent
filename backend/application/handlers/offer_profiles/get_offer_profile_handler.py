from di.container import Container
from application.mappers.offer_profile_mapper import OfferProfileMapper


# =====================================================
# MAIN HANDLER
# =====================================================

def get_offer_profile_handler(
    offer_profile_id: int
):
    container = Container()

    offer_profile_repository = (
        container.offer_profile_repository()
    )

    offer_profile_assembler = (
        container.offer_profile_assembler()
    )


    item = offer_profile_repository.get_by_id(
        offer_profile_id
    )

    if not item:
        raise ValueError(
            f"OfferProfile {offer_profile_id} not found"
        )


    item_dto = OfferProfileMapper.to_dto(
        item
    )


    result = offer_profile_assembler.assemble_dto(
        item_dto
    )


    return result

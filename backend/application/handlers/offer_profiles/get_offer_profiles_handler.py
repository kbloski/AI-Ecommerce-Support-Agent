from di.container import Container
from application.mappers.offer_profile_mapper import OfferProfileMapper


# =====================================================
# MAIN HANDLER
# =====================================================

def get_offer_profiles_handler(
    offer_id: int,
):
    container = Container()

    offer_profile_repository = (
        container.offer_profile_repository()
    )


    items = offer_profile_repository.get_by_offer_id(
        offer_id
    )

    dtos = [
        OfferProfileMapper.to_dto(item)
        for item in items
    ]

    return dtos

from di.container import Container


def get_offer_profile_brand_marketings_handler(
    offer_profile_id: int,
):
    container = Container()

    brand_marketing_service = container.brand_marketing_service()

    return brand_marketing_service.get_brand_marketings_by_offer_profile(offer_profile_id=offer_profile_id)

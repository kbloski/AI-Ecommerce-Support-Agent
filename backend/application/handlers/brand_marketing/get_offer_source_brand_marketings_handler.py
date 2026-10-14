from di.container import Container


def get_offer_source_brand_marketings_handler(
    offer_source_id: int,
):
    container = Container()

    brand_marketing_service = container.brand_marketing_service()

    return brand_marketing_service.get_brand_marketings_by_offer_source(offer_source_id=offer_source_id)

from di.container import Container


def get_offer_profile_page_blueprint_handler(offer_profile_id: int):
    container = Container()
    page_blueprint_service = container.page_blueprint_service()
    return page_blueprint_service.get_page_blueprint_by_offer_profile(
        offer_profile_id=offer_profile_id
    )

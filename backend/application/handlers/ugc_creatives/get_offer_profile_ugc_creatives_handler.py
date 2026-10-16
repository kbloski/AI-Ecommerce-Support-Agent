from di.container import Container


def get_offer_profile_ugc_creatives_handler(
    offer_profile_id: int,
):
    container = Container()
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise LookupError("Offer profile not found")

    ugc_creative_service = container.ugc_creative_service()

    return ugc_creative_service.get_ugc_creatives_by_offer_profile(
        offer_profile_id=offer_profile_id
    )

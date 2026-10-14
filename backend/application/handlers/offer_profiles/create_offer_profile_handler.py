from fastapi import HTTPException
from di.container import Container
from application.mappers.offer_profile_mapper import offer_profile_to_dict
from domain.models.offer.offer_profile import OfferProfile


def create_offer_profile_handler(offer_source_id: int, name: str):
    container = Container()
    if container.offer_source_repository().get_by_id(offer_source_id) is None:
        raise HTTPException(404, "Offer source not found")
    profile = OfferProfile(offer_source_id=offer_source_id, name=name)
    return offer_profile_to_dict(container.offer_profiles_repository().create(profile))

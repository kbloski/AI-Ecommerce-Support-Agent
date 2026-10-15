from fastapi import HTTPException
from di.container import Container
from application.mappers.offer_profile_mapper import offer_profile_to_dict


def list_all_offer_profiles_handler():
    return [offer_profile_to_dict(profile) for profile in Container().offer_profiles_repository().find_all()]


def list_offer_profiles_handler(offer_source_id: int):
    container = Container()
    if container.offer_source_repository().get_by_id(offer_source_id) is None:
        raise HTTPException(404, "Offer source not found")
    return [offer_profile_to_dict(profile) for profile in container.offer_profiles_repository().find_for_offer_source(offer_source_id)]

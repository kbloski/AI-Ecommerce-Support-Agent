from fastapi import HTTPException
from di.container import Container
from application.mappers.offer_profile_mapper import offer_profile_to_dict


def get_offer_profile_handler(id: int):
    repo = Container().offer_profiles_repository()
    profile = repo.get_by_id(id)
    if profile is None:
        raise HTTPException(404, "Offer profile not found")
    return offer_profile_to_dict(profile)

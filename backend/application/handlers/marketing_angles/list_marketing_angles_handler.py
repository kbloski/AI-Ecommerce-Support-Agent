from fastapi import HTTPException

from application.mappers.marketing_angle_mapper import marketing_angle_to_dict
from di.container import Container


def list_marketing_angles_handler(offer_profile_id: int):
    container = Container()
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")
    return [marketing_angle_to_dict(item) for item in container.marketing_angles_repository().find_for_offer_profile(offer_profile_id)]

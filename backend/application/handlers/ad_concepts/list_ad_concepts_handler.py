from fastapi import HTTPException

from application.mappers.ad_concept_mapper import ad_concept_to_dict
from di.container import Container


def list_ad_concepts_handler(offer_profile_id: int):
    container = Container()
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")
    return [ad_concept_to_dict(item) for item in container.ad_concepts_repository().find_for_offer_profile(offer_profile_id)]

from fastapi import HTTPException

from application.dtos.ad_concepts.ad_concept_fields import CreateAdConceptRequest
from application.mappers.ad_concept_mapper import ad_concept_to_dict
from di.container import Container
from domain.models.ad.ad_concept import AdConcept


def create_ad_concept_handler(offer_profile_id: int, fields: CreateAdConceptRequest):
    container = Container()
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")
    if fields.marketing_angle_id is not None:
        angle = container.marketing_angles_repository().get_by_id(fields.marketing_angle_id)
        if angle is None:
            raise HTTPException(404, "Marketing angle not found")
        if angle.offer_profile_id != offer_profile_id:
            raise HTTPException(422, "Selected marketing angle must belong to this offer profile")
    item = AdConcept(offer_profile_id=offer_profile_id, **fields.model_dump())
    return ad_concept_to_dict(container.ad_concepts_repository().create_many([item])[0])

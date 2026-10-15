from fastapi import HTTPException

from application.dtos.ad_concepts.ad_concept_fields import CreateAdConceptRequest
from application.mappers.ad_concept_mapper import ad_concept_to_dict
from di.container import Container
from domain.models.ad.ad_concept import AdConcept


def create_ad_concept_handler(offer_profile_id: int, fields: CreateAdConceptRequest):
    container = Container()
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")
    try:
        angles = container.marketing_angle_service().get_selected_angles(
            offer_profile_id, fields.marketing_angle_ids,
        )
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    item = AdConcept(
        offer_profile_id=offer_profile_id,
        generation_mode=fields.generation_mode.value,
        marketing_angles=angles,
        **fields.model_dump(exclude={"generation_mode", "marketing_angle_ids"}),
    )
    return ad_concept_to_dict(container.ad_concepts_repository().create_many([item])[0])

from fastapi import HTTPException

from application.dtos.ad_concepts.ad_concept_fields import UpdateAdConceptRequest
from application.mappers.ad_concept_mapper import ad_concept_to_dict
from di.container import Container


def update_ad_concept_handler(id: int, fields: UpdateAdConceptRequest):
    container = Container()
    repo = container.ad_concepts_repository()
    item = repo.get_by_id(id)
    if item is None:
        raise HTTPException(404, "Ad concept not found")
    if fields.marketing_angle_id is not None:
        angle = container.marketing_angles_repository().get_by_id(fields.marketing_angle_id)
        if angle is None:
            raise HTTPException(404, "Marketing angle not found")
        if angle.offer_profile_id != item.offer_profile_id:
            raise HTTPException(422, "Selected marketing angle must belong to this offer profile")
    values = fields.model_dump(exclude={"is_reviewed"})
    if any(getattr(item, key) != value for key, value in values.items()):
        item.is_reviewed = False
    else:
        item.is_reviewed = fields.is_reviewed
    for key, value in values.items():
        setattr(item, key, value)
    return ad_concept_to_dict(repo.update(item))

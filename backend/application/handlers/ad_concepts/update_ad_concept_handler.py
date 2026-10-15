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
    selection_provided = bool({"generation_mode", "marketing_angle_ids"} & fields.model_fields_set)
    if selection_provided:
        try:
            angles = container.marketing_angle_service().get_selected_angles(
                item.offer_profile_id, fields.marketing_angle_ids,
            )
        except LookupError as error:
            raise HTTPException(404, str(error)) from error
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
    else:
        angles = item.marketing_angles
    mode = fields.generation_mode.value if selection_provided else item.generation_mode
    values = fields.model_dump(exclude={"is_reviewed", "generation_mode", "marketing_angle_ids"})
    changed = (
        any(getattr(item, key) != value for key, value in values.items())
        or item.generation_mode != mode
        or sorted(angle.id for angle in item.marketing_angles) != sorted(angle.id for angle in angles)
    )
    if changed:
        item.is_reviewed = False
    else:
        item.is_reviewed = fields.is_reviewed
    for key, value in values.items():
        setattr(item, key, value)
    item.generation_mode = mode
    item.marketing_angles = angles
    return ad_concept_to_dict(repo.update(item))

from fastapi import HTTPException

from application.dtos.marketing_angles.marketing_angle_fields import UpdateMarketingAngleRequest
from application.mappers.marketing_angle_mapper import marketing_angle_to_dict
from di.container import Container


def update_marketing_angle_handler(id: int, fields: UpdateMarketingAngleRequest):
    repo = Container().marketing_angles_repository()
    item = repo.get_by_id(id)
    if item is None:
        raise HTTPException(404, "Marketing angle not found")
    values = fields.model_dump(exclude={"is_reviewed"})
    if any(getattr(item, key) != value for key, value in values.items()):
        item.is_reviewed = False
    else:
        item.is_reviewed = fields.is_reviewed
    for key, value in values.items():
        setattr(item, key, value)
    return marketing_angle_to_dict(repo.update(item))

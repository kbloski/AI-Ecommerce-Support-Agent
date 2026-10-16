from di.container import Container
from application.mappers.ugc_creative_mapper import UgcCreativeMapper
from application.dtos.ugc_creatives.ugc_generation_fields import UgcGenerationFields
from fastapi import HTTPException
from pydantic import StrictBool, TypeAdapter, ValidationError


def update_ugc_creative_handler(id: int, fields: dict):
    container = Container()
    repository = container.ugc_creative_repository()
    creative = repository.get_by_id(id)
    if creative is None:
        raise HTTPException(404, "UGC creative not found")

    content_keys = set(UgcGenerationFields.model_fields)
    if set(fields) - content_keys - {"is_reviewed"}:
        raise HTTPException(422, "Unsupported UGC fields")
    values = {key: value for key, value in fields.items() if key in content_keys}
    for key, value in list(values.items()):
        if value is None and key != "name":
            values[key] = {} if key == "customer_persona" else [] if key in {"video_flow", "platform_fit"} else ""
    try:
        validated = UgcGenerationFields.model_validate({"name": creative.name or "UGC", **values})
        values = validated.model_dump(include=set(values))
        reviewed = TypeAdapter(StrictBool).validate_python(fields.get("is_reviewed", creative.is_reviewed))
    except (ValidationError, ValueError, TypeError) as error:
        raise HTTPException(422, "Invalid UGC content or review state") from error
    changed = any(getattr(creative, key) != value for key, value in values.items())
    for key, value in values.items():
        setattr(creative, key, value)
    creative.is_reviewed = False if changed else reviewed

    return UgcCreativeMapper.to_dto(repository.update(creative)).to_dict()

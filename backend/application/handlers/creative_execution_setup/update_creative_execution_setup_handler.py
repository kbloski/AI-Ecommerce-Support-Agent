from di.container import Container
from application.mappers.creative_execution_setup_mapper import CreativeExecutionSetupMapper


ALLOWED_FIELDS = {
    "name", "duration_seconds", "number_of_slides", "ad_framework_id",
    "creative_angle_id", "execution_style_id", "additional_instructions",
    "is_favorite",
}


def update_creative_execution_setup_handler(id: int, fields: dict):
    repository = Container().creative_execution_setup_repository()
    item = repository.get_by_id(id)
    if item is None:
        raise LookupError(f"Creative Execution Setup {id} not found")
    for key, value in fields.items():
        if key in ALLOWED_FIELDS:
            setattr(item, key, value)
    return CreativeExecutionSetupMapper.to_dto(repository.update(item)).to_dict()

from typing import Any, Dict

from di.container import Container
from application.mappers.generate_ad_mapper import GenerateAdMapper

DENYLIST = {"id", "creative_execution_setup_id", "created_at", "updated_at"}


def update_generate_ad_handler(id: int, fields: Dict[str, Any]):
    container = Container()
    generate_ad_repository = container.generate_ad_repository()

    item = generate_ad_repository.get_by_id(id)

    for key, value in fields.items():
        if key not in DENYLIST:
            setattr(item, key, value)

    updated = generate_ad_repository.update(item)
    return GenerateAdMapper.to_dto(updated).to_dict()

from typing import Any, Dict

from di.container import Container
from application.mappers.ad_setup_mapper import AdSetupMapper
from domain.enums.creative_types import CreativeTypes

ALLOWED_FIELDS = {"name", "creative_type", "platform", "format", "is_favorite"}


def update_ad_setup_handler(id: int, fields: Dict[str, Any]):
    container = Container()
    ad_setup_repository = container.ad_setup_repository()

    item = ad_setup_repository.get_by_id(id)
    if item is None:
        raise LookupError(f"Ad Setup {id} not found")

    if "creative_type" in fields and fields["creative_type"] not in {item.value for item in CreativeTypes}:
        raise ValueError(f"Unsupported creative type: {fields['creative_type']}")
    if "platform" in fields and container.platforms_repository().get_by_id(fields["platform"]) is None:
        raise ValueError(f"Unsupported platform: {fields['platform']}")

    for key, value in fields.items():
        if key in ALLOWED_FIELDS:
            setattr(item, key, value)

    updated = ad_setup_repository.update(item)
    return AdSetupMapper.to_dto(updated).to_dict()

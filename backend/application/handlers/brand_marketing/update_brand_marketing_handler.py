from typing import Any, Dict

from di.container import Container
from application.mappers.brand_marketing_mapper import BrandMarketingMapper

DENYLIST = {"id", "offer_profile_id", "created_at", "updated_at"}


def update_brand_marketing_handler(id: int, fields: Dict[str, Any]):
    container = Container()
    brand_marketing_repository = container.brand_marketing_repository()

    item = brand_marketing_repository.get_by_id(id)

    for key, value in fields.items():
        if key not in DENYLIST:
            setattr(item, key, value)

    updated = brand_marketing_repository.update(item)
    return BrandMarketingMapper.to_dto(updated).to_dict()

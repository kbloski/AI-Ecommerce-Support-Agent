from typing import Any, Dict

from di.container import Container
from application.mappers.offer_profile_mapper import OfferProfileMapper

DENYLIST = {"id", "offer_id", "created_at", "updated_at"}


def update_offer_profile_handler(id: int, fields: Dict[str, Any]):
    container = Container()
    offer_profile_repository = container.offer_profile_repository()
    offer_profile_assembler = container.offer_profile_assembler()

    item = offer_profile_repository.get_by_id(id)

    for key, value in fields.items():
        if key not in DENYLIST:
            setattr(item, key, value)

    updated = offer_profile_repository.update(item)
    dto = OfferProfileMapper.to_dto(updated)
    return offer_profile_assembler.assemble_dto(dto)

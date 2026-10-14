from typing import Any, Dict

from di.container import Container
from application.mappers.offer_source_mapper import OfferSourceMapper

DENYLIST = {"id", "offer_id", "created_at", "updated_at"}


def update_offer_source_handler(id: int, fields: Dict[str, Any]):
    container = Container()
    offer_source_repository = container.offer_source_repository()
    offer_source_assembler = container.offer_source_assembler()

    item = offer_source_repository.get_by_id(id)

    for key, value in fields.items():
        if key not in DENYLIST:
            setattr(item, key, value)

    updated = offer_source_repository.update(item)
    dto = OfferSourceMapper.to_dto(updated)
    return offer_source_assembler.assemble_dto(dto)

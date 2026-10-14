from typing import Any, Dict

from di.container import Container
from application.mappers.offer_source_element_mapper import OfferSourceElementMapper

DENYLIST = {"id", "offer_source_id", "created_at", "updated_at"}


def update_offer_source_element_handler(id: int, fields: Dict[str, Any]) -> dict:
    container = Container()
    offer_source_elements_repository = container.offer_source_elements_repository()

    item = offer_source_elements_repository.get_by_id(id)
    if item is None:
        raise LookupError(f"OfferSourceElement with id {id} not found")

    for key, value in fields.items():
        if key not in DENYLIST:
            setattr(item, key, value)

    updated = offer_source_elements_repository.update(item)
    return OfferSourceElementMapper.to_dto(updated).to_dict()

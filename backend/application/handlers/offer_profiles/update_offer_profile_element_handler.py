from typing import Any, Dict

from di.container import Container
from application.mappers.offer_profile_element_mapper import OfferProfileElementMapper

DENYLIST = {"id", "offer_profile_id", "created_at", "updated_at"}


def update_offer_profile_element_handler(id: int, fields: Dict[str, Any]) -> dict:
    container = Container()
    offer_profile_elements_repository = container.offer_profile_elements_repository()

    item = offer_profile_elements_repository.get_by_id(id)
    if item is None:
        raise LookupError(f"OfferProfileElement with id {id} not found")

    for key, value in fields.items():
        if key not in DENYLIST:
            setattr(item, key, value)

    updated = offer_profile_elements_repository.update(item)
    return OfferProfileElementMapper.to_dto(updated).to_dict()

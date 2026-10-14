from di.container import Container
from application.mappers.offer_source_element_mapper import OfferSourceElementMapper
from domain.enums.offer_source_element_type import OfferSourceElementType
from domain.models.offer.offer_source_element import OfferSourceElement


def create_offer_source_element_handler(
    offer_source_id: int,
    element_type: OfferSourceElementType,
    name: str,
    description: str | None,
    is_reviewed: bool = False,
) -> dict:
    container = Container()
    if container.offer_source_repository().get_by_id(offer_source_id) is None:
        raise LookupError(f"OfferSource with id {offer_source_id} not found")

    element = OfferSourceElement(
        offer_source_id=offer_source_id,
        type=element_type,
        name=name,
        description=description or None,
        is_reviewed=is_reviewed,
    )
    created = container.offer_source_elements_repository().create(element)
    return OfferSourceElementMapper.to_dto(created).to_dict()

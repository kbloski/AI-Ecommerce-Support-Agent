from di.container import Container
from application.mappers.offer_profile_element_mapper import OfferProfileElementMapper
from domain.enums.offer_profile_element_type import OfferProfileElementType
from domain.models.offer_profiles.offer_profile_element import OfferProfileElement


def create_offer_profile_element_handler(
    offer_profile_id: int,
    element_type: OfferProfileElementType,
    name: str,
    description: str | None,
) -> dict:
    container = Container()
    if container.offer_profile_repository().get_by_id(offer_profile_id) is None:
        raise LookupError(f"OfferProfile with id {offer_profile_id} not found")

    element = OfferProfileElement(
        offer_profile_id=offer_profile_id,
        type=element_type,
        name=name,
        description=description or None,
    )
    created = container.offer_profile_elements_repository().create(element)
    return OfferProfileElementMapper.to_dto(created).to_dict()

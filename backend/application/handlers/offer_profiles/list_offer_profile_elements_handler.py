from di.container import Container
from application.mappers.offer_profile_element_mapper import OfferProfileElementMapper


def list_offer_profile_elements_handler(offer_profile_id: int) -> list[dict]:
    container = Container()
    elements = container.offer_profile_elements_repository().find_for_offer_profile(
        offer_profile_id
    )
    return [OfferProfileElementMapper.to_dto(element).to_dict() for element in elements]

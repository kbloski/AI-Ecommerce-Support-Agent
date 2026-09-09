from domain.enums.offer_profile_element_type import OfferProfileElementType


def list_offer_profile_element_types_handler() -> list[str]:
    return [element_type.value for element_type in OfferProfileElementType]

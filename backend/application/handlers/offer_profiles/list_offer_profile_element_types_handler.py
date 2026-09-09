from domain.enums.offer_profile_element_type import get_offer_profile_element_type_values


def list_offer_profile_element_types_handler() -> list[str]:
    return get_offer_profile_element_type_values()

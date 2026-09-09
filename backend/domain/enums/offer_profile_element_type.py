try:
    from enum import StrEnum
except ImportError:  # Python 3.10 compatibility
    from enum import Enum

    class StrEnum(str, Enum):
        pass


class OfferProfileElementType(StrEnum):
    BENEFIT = "benefit"
    FEATURE = "feature"
    PROBLEM_SOLVED = "problem_solved"
    USE_CASE = "use_case"
    DIFFERENTIATOR = "differentiator"
    LIMITATION = "limitation"


def get_offer_profile_element_type_values() -> list[str]:
    return [element_type.value for element_type in OfferProfileElementType]

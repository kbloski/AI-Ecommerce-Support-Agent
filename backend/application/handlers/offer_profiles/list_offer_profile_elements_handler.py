from di.container import Container
from application.mappers.offer_profile_element_mapper import OfferProfileElementMapper
from domain.enums.offer_profile_element_type import OfferProfileElementType


def list_offer_profile_elements_handler(
    offer_profile_id: int,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    element_type: OfferProfileElementType | None = None,
    is_reviewed: bool | None = None,
    sort: str = "created_at_desc",
) -> dict:
    container = Container()
    result = container.offer_profile_elements_repository().search_for_offer_profile(
        offer_profile_id=offer_profile_id,
        page=page,
        page_size=page_size,
        search=search,
        element_type=element_type,
        is_reviewed=is_reviewed,
        sort=sort,
    )
    return result.to_dict(
        lambda element: OfferProfileElementMapper.to_dto(element).to_dict()
    )

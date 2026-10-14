from di.container import Container
from application.mappers.offer_source_element_mapper import OfferSourceElementMapper
from domain.enums.offer_source_element_type import OfferSourceElementType


def list_offer_source_elements_handler(
    offer_source_id: int,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    element_type: OfferSourceElementType | None = None,
    is_reviewed: bool | None = None,
    sort: str = "created_at_desc",
) -> dict:
    container = Container()
    result = container.offer_source_elements_repository().search_for_offer_source(
        offer_source_id=offer_source_id,
        page=page,
        page_size=page_size,
        search=search,
        element_type=element_type,
        is_reviewed=is_reviewed,
        sort=sort,
    )
    return result.to_dict(
        lambda element: OfferSourceElementMapper.to_dto(element).to_dict()
    )

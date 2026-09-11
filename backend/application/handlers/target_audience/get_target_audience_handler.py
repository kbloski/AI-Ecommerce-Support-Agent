from typing import Literal
from di.container import Container
from application.mappers.target_audience_mapper import TargetAudienceMapper

def get_target_audience_handler(
    offer_profile_id: int,
    page: int = 1,
    page_size: int = 20,
    is_reviewed: bool | None = None,
    sort: Literal["unreviewed_first", "reviewed_first"] = "unreviewed_first",
) -> dict:
    container = Container()

    target_audiences_repository = container.target_audiences_repository()

    result = target_audiences_repository.search_for_offer_profile(
        offer_profile_id=offer_profile_id,
        page=page,
        page_size=page_size,
        is_reviewed=is_reviewed,
        sort=sort,
    )

    return result.to_dict(
        lambda item: TargetAudienceMapper.to_dto(item).to_dict()
    )

from di.container import Container

from domain.models.ad_setup.ad_setup import AdSetup
from domain.enums.enums import CreativeTypes

ALLOWED_CREATIVE_TYPES = [item.value for item in CreativeTypes]


def create_ad_setup_handler(
    creative_strategy_id: int,
    creative_type: str,
    platform: str,
    format: str,
    name: str | None = None
):

    if creative_type not in ALLOWED_CREATIVE_TYPES:
        raise ValueError(
            f"Unsupported creative type: {creative_type}"
        )

    container = Container()

    if container.platforms_repository().get_by_id(platform) is None:
        raise ValueError(f"Unsupported platform: {platform}")


    ad_setup_service = (
        container.ad_setup_service()
    )


    entity = AdSetup(

        creative_strategy_id=creative_strategy_id,

        name=name or (
            f"{creative_type.capitalize()} Ad Setup"
        ),

        creative_type=creative_type,

        platform=platform,

        format=format

    )


    return ad_setup_service.create_ad_setup(entity)

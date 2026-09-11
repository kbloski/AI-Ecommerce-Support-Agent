from di.container import Container


def get_creative_strategy_ad_setups_handler(
    creative_strategy_id: int,
):
    container = Container()

    ad_setup_service = container.ad_setup_service()

    return ad_setup_service.get_ad_setups_by_creative_strategy(
        creative_strategy_id=creative_strategy_id
    )

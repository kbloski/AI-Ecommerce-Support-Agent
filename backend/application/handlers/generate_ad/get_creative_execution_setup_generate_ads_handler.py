from di.container import Container


def get_creative_execution_setup_generate_ads_handler(
    creative_execution_setup_id: int,
):
    container = Container()

    generate_ad_service = container.generate_ad_service()

    return generate_ad_service.get_generate_ads_by_setup(
        creative_execution_setup_id=creative_execution_setup_id
    )

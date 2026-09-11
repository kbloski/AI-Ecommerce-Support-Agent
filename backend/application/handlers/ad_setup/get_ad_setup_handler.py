from di.container import Container


def get_ad_setup_handler(
    id: int,
):
    container = Container()

    ad_setup_service = container.ad_setup_service()

    return ad_setup_service.get_ad_setup_by_id(id=id)

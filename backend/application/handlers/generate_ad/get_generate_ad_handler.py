from di.container import Container


def get_generate_ad_handler(
    id: int,
):
    container = Container()

    generate_ad_service = container.generate_ad_service()

    return generate_ad_service.get_generate_ad_by_id(id=id)

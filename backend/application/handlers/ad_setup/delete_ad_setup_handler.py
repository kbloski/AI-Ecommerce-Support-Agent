from di.container import Container


def delete_ad_setup_handler(id: int):
    container = Container()
    ad_setup_repository = container.ad_setup_repository()

    deleted = ad_setup_repository.delete(id=id)

    return {"deleted": deleted}

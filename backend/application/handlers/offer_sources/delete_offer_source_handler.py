from di.container import Container


def delete_offer_source_handler(id: int):
    container = Container()
    offer_source_repository = container.offer_source_repository()

    deleted = offer_source_repository.delete(id=id)

    return {"deleted": deleted}

from di.container import Container


def delete_offer_handler(id: int):
    container = Container()
    offers_repository = container.offers_repository()
    deleted = offers_repository.delete(id=id)

    return {"deleted": deleted}

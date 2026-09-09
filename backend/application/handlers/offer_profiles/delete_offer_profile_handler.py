from di.container import Container


def delete_offer_profile_handler(id: int):
    container = Container()
    offer_profile_repository = container.offer_profile_repository()

    deleted = offer_profile_repository.delete(id=id)

    return {"deleted": deleted}

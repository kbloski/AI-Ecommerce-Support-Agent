from di.container import Container


def delete_offer_profile_element_handler(id: int):
    container = Container()
    offer_profile_elements_repository = container.offer_profile_elements_repository()

    deleted = offer_profile_elements_repository.delete(id=id)

    return {"deleted": deleted}

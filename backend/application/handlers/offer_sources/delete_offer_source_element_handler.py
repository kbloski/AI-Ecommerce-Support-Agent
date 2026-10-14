from di.container import Container


def delete_offer_source_element_handler(id: int):
    container = Container()
    offer_source_elements_repository = container.offer_source_elements_repository()

    deleted = offer_source_elements_repository.delete(id=id)

    return {"deleted": deleted}

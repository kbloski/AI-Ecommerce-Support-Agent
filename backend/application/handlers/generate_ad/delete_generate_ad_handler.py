from di.container import Container


def delete_generate_ad_handler(id: int):
    container = Container()
    generate_ad_repository = container.generate_ad_repository()

    deleted = generate_ad_repository.delete(id=id)

    return {"deleted": deleted}

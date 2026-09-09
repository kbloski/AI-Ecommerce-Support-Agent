from di.container import Container

def get_offers(page : int):
    container = Container()
    offers_repository = container.offers_repository()
    result = offers_repository.search(
        page=page
    )
    return result



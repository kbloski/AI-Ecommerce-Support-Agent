from fastapi import HTTPException

from di.container import Container


def get_pages_handler(offer_profile_id: int):
    container = Container()
    try:
        container.offer_profile_service().get_offer_profile_details_by_id(offer_profile_id)
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    return container.page_service().get_by_offer_profile_id(offer_profile_id)


def get_page_handler(page_id: int):
    try:
        return Container().page_service().get_by_id(page_id)
    except LookupError as error:
        raise HTTPException(404, str(error)) from error


def delete_page_handler(page_id: int):
    if not Container().page_repository().delete(page_id):
        raise HTTPException(404, f"Page {page_id} not found")
    return {"deleted": True}

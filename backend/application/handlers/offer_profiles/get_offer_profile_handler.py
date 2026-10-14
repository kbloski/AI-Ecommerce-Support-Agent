from fastapi import HTTPException
from di.container import Container


def get_offer_profile_handler(id: int):
    try:
        return Container().offer_profile_service().get_offer_profile_details_by_id(id).to_dict()
    except LookupError as error:
        raise HTTPException(404, str(error)) from error

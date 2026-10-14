from fastapi import HTTPException
from di.container import Container
from application.mappers.additional_context_mapper import additional_context_to_dict


def list_additional_contexts_handler(offer_profile_id: int | None = None):
    container = Container()
    repo = container.additional_contexts_repository()
    if offer_profile_id is None:
        contexts = repo.list_all()
    else:
        if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
            raise HTTPException(404, "Offer profile not found")
        contexts = repo.find_for_offer_profile(offer_profile_id)
    return [additional_context_to_dict(context) for context in contexts]

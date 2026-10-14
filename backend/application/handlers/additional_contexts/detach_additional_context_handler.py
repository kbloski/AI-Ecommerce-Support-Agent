from fastapi import HTTPException
from di.container import Container
from application.mappers.additional_context_mapper import additional_context_to_dict


def detach_additional_context_handler(offer_profile_id: int, additional_context_id: int):
    container = Container()
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")
    repo = container.additional_contexts_repository()
    if repo.get_by_id(additional_context_id) is None:
        raise HTTPException(404, "Additional context not found")
    repo.detach(offer_profile_id, additional_context_id)
    return {"detached": True}

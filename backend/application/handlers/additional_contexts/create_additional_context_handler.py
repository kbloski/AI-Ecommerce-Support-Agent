from fastapi import HTTPException
from di.container import Container
from application.mappers.additional_context_mapper import additional_context_to_dict
from domain.models.context.additional_context import AdditionalContext


def create_additional_context_handler(offer_profile_id: int, name: str, content: str):
    container = Container()
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")
    context = AdditionalContext(name=name, content=content)
    return additional_context_to_dict(container.additional_contexts_repository().create_for_offer_profile(offer_profile_id, context))

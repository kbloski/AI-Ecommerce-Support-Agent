from application.mappers.additional_context_mapper import additional_context_to_dict
from application.dtos.offer_profiles.offer_profile_dto import OfferProfileDto
from infrastructure.repositories.additional_contexts_repository import AdditionalContextsRepository


class OfferProfileAssembler:
    def __init__(self, additional_contexts_repository: AdditionalContextsRepository):
        self.additional_contexts_repository = additional_contexts_repository

    def assemble_dto(self, item: OfferProfileDto) -> OfferProfileDto:
        contexts = self.additional_contexts_repository.find_for_offer_profile(item.id)
        item.additional_contexts = [additional_context_to_dict(context) for context in contexts]
        return item

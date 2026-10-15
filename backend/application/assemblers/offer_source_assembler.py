from application.dtos.offer_sources.offer_source_dto import OfferSourceDto
from application.mappers.offer_source_element_mapper import OfferSourceElementMapper
from infrastructure.logging.logger import Logger
from infrastructure.repositories.offer_source_repository import OfferSourceRepository
from infrastructure.repositories.offer_source_elements_repository import OfferSourceElementsRepository
from infrastructure.repositories.offer_facts_repository import OfferFactsRepository
from application.mappers.offer_fact_mapper import offer_fact_to_dict

class OfferSourceAssembler:
    def __init__(
        self,
        logger : Logger,
        offer_source_repository : OfferSourceRepository,
        offer_facts_repository: OfferFactsRepository,
        offer_source_elements_repository : OfferSourceElementsRepository
    ):
        self.offer_facts_repository = offer_facts_repository
        self.offer_source_repository = offer_source_repository
        self.offer_source_elements_repository = offer_source_elements_repository

    def assemble_dto(self, item : OfferSourceDto) -> OfferSourceDto:
        # item

        offer_source_elements = self.offer_source_elements_repository.find_for_offer_source(
            offer_source_id=item.id
        )
        item.offer_source_elements = [
            OfferSourceElementMapper.to_dto(element)
            for element in offer_source_elements
        ]

        item.offer_facts = [offer_fact_to_dict(fact) for fact in self.offer_facts_repository.find_for_offer_source(item.id)]
        return item

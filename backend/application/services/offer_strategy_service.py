import json

from typing import List

from infrastructure.logging.logger import Logger
from domain.models.offer.offer_strategy import OfferStrategy
from application.dtos.offer_strategy.offer_strategy_response_dto import OfferStrategyDto
from infrastructure.repositories.offer_strategy_repository import OfferStrategyRepository
from application.mappers.offer_strategy_mapper import OfferStrategyMapper
from application.assemblers.offer_strategy_assembler import OfferStrategyAssembler
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class OfferStrategyService:

    def __init__(
        self,
        logger: Logger,
        offer_strategy_repository: OfferStrategyRepository,
        offer_strategy_assembler: OfferStrategyAssembler,
    ):
        self.logger = logger
        self.offer_strategy_repository = offer_strategy_repository
        self.offer_strategy_assembler = offer_strategy_assembler

    def create_offer_strategy(self, offer_strategy: OfferStrategy) -> OfferStrategyDto:
        created = self.offer_strategy_repository.create(offer_strategy)
        return self.get_offer_strategy_by_id(id=created.id)

    def get_offer_strategy_by_id(self, id: int) -> OfferStrategyDto:
        offer_strategy_db = self.offer_strategy_repository.get_by_id(id)

        if not offer_strategy_db:
            raise ValueError(f"Offer strategy {id} not found")

        offer_strategy_dto = OfferStrategyMapper.to_dto(offer_strategy_db)
        return self.offer_strategy_assembler.assemble_dto(offer_strategy_dto)

    def get_offer_strategies_by_marketing_strategy(self, marketing_strategy_id: int) -> List[OfferStrategyDto]:
        items = self.offer_strategy_repository.get_by_marketing_strategy_id(marketing_strategy_id)
        dtos = [OfferStrategyMapper.to_dto(item) for item in items]
        return [self.offer_strategy_assembler.assemble_dto(dto) for dto in dtos]

    def build_llm_context(self, offer_strategy_id: int) -> str:
        offer_strategy_json = json.dumps(
            self.get_offer_strategy_by_id(id=offer_strategy_id).to_content_dict(),
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section("offer-strategy", offer_strategy_json, purpose=ContextSectionPurpose.OFFER_STRATEGY.value)

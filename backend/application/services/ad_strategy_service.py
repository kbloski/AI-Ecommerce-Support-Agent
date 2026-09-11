import json

from typing import List

from infrastructure.logging.logger import Logger
from domain.models.ad_strategy.ad_strategy import AdStrategy
from application.dtos.ad_strategy.ad_strategy_response_dto import AdStrategyDto
from infrastructure.repositories.ad_strategy_repository import AdStrategyRepository
from application.mappers.ad_strategy_mapper import AdStrategyMapper
from application.assemblers.ad_strategy_assembler import AdStrategyAssembler
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class AdStrategyService:

    def __init__(
        self,
        logger: Logger,
        ad_strategy_repository: AdStrategyRepository,
        ad_strategy_assembler: AdStrategyAssembler,
    ):
        self.logger = logger
        self.ad_strategy_repository = ad_strategy_repository
        self.ad_strategy_assembler = ad_strategy_assembler

    def create_ad_strategy(self, ad_strategy: AdStrategy) -> AdStrategyDto:
        created = self.ad_strategy_repository.create(ad_strategy)
        return self.get_ad_strategy_by_id(id=created.id)

    def get_ad_strategy_by_id(self, id: int) -> AdStrategyDto:
        ad_strategy_db = self.ad_strategy_repository.get_by_id(id)

        if not ad_strategy_db:
            raise ValueError(f"Ad strategy {id} not found")

        ad_strategy_dto = AdStrategyMapper.to_dto(ad_strategy_db)
        return self.ad_strategy_assembler.assemble_dto(ad_strategy_dto)

    def get_ad_strategies_by_message_strategy(self, message_strategy_id: int) -> List[AdStrategyDto]:
        items = self.ad_strategy_repository.get_by_message_strategy_id(message_strategy_id)
        dtos = [AdStrategyMapper.to_dto(item) for item in items]
        return [self.ad_strategy_assembler.assemble_dto(dto) for dto in dtos]

    def build_llm_context(self, ad_strategy_id: int) -> str:
        ad_strategy_json = json.dumps(
            self.get_ad_strategy_by_id(id=ad_strategy_id).to_content_dict(),
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section(
            "ad-strategy",
            ad_strategy_json,
            purpose=ContextSectionPurpose.AD_STRATEGY.value,
        )

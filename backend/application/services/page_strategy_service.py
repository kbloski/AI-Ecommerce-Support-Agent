import json

from typing import List

from infrastructure.logging.logger import Logger
from domain.models.page.page_strategy import PageStrategy
from application.dtos.page_strategy.page_strategy_response_dto import PageStrategyDto
from infrastructure.repositories.page_strategy_repository import PageStrategyRepository
from application.mappers.page_strategy_mapper import PageStrategyMapper
from application.assemblers.page_strategy_assembler import PageStrategyAssembler
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class PageStrategyService:

    def __init__(
        self,
        logger: Logger,
        page_strategy_repository: PageStrategyRepository,
        page_strategy_assembler: PageStrategyAssembler,
    ):
        self.logger = logger
        self.page_strategy_repository = page_strategy_repository
        self.page_strategy_assembler = page_strategy_assembler

    def create_page_strategy(self, page_strategy: PageStrategy) -> PageStrategyDto:
        created = self.page_strategy_repository.create(page_strategy)
        return self.get_page_strategy_by_id(id=created.id)

    def get_page_strategy_by_id(self, id: int) -> PageStrategyDto:
        page_strategy_db = self.page_strategy_repository.get_by_id(id)

        if not page_strategy_db:
            raise ValueError(f"Page strategy {id} not found")

        page_strategy_dto = PageStrategyMapper.to_dto(page_strategy_db)
        return self.page_strategy_assembler.assemble_dto(page_strategy_dto)

    def get_page_strategies_by_message_strategy(self, message_strategy_id: int) -> List[PageStrategyDto]:
        items = self.page_strategy_repository.get_by_message_strategy_id(message_strategy_id)
        dtos = [PageStrategyMapper.to_dto(item) for item in items]
        return [self.page_strategy_assembler.assemble_dto(dto) for dto in dtos]

    def build_llm_context(self, page_strategy_id: int) -> str:
        page_strategy_json = json.dumps(
            self.get_page_strategy_by_id(id=page_strategy_id).to_content_dict(),
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section(
            "page-strategy",
            page_strategy_json,
            purpose=ContextSectionPurpose.PAGE_STRATEGY.value,
        )

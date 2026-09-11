import json

from typing import List

from infrastructure.logging.logger import Logger
from domain.models.ad_setup.ad_setup import AdSetup
from application.dtos.ad_setup.ad_setup_response_dto import AdSetupDto
from infrastructure.repositories.ad_setup_repository import AdSetupRepository
from application.mappers.ad_setup_mapper import AdSetupMapper
from application.assemblers.ad_setup_assembler import AdSetupAssembler
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class AdSetupService:

    def __init__(
        self,
        logger: Logger,
        ad_setup_repository: AdSetupRepository,
        ad_setup_assembler: AdSetupAssembler,
    ):
        self.logger = logger
        self.ad_setup_repository = ad_setup_repository
        self.ad_setup_assembler = ad_setup_assembler

    def create_ad_setup(self, ad_setup: AdSetup) -> AdSetupDto:
        created = self.ad_setup_repository.create(ad_setup)
        return self.get_ad_setup_by_id(id=created.id)

    def get_ad_setup_by_id(self, id: int) -> AdSetupDto:
        ad_setup_db = self.ad_setup_repository.get_by_id(id)

        if not ad_setup_db:
            raise ValueError(f"Ad Setup {id} not found")

        ad_setup_dto = AdSetupMapper.to_dto(ad_setup_db)
        return self.ad_setup_assembler.assemble_dto(ad_setup_dto)

    def get_ad_setups_by_creative_strategy(self, creative_strategy_id: int) -> List[AdSetupDto]:
        items = self.ad_setup_repository.get_by_creative_strategy_id(creative_strategy_id)
        dtos = [AdSetupMapper.to_dto(item) for item in items]
        return [self.ad_setup_assembler.assemble_dto(dto) for dto in dtos]

    def build_llm_context(self, ad_setup_id: int) -> str:
        ad_setup_json = json.dumps(
            self.get_ad_setup_by_id(id=ad_setup_id).to_content_dict(),
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section(
            "ad-setup",
            ad_setup_json,
            purpose=ContextSectionPurpose.AD_SETUP.value,
        )

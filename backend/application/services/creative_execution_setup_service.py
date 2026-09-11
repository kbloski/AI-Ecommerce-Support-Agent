import json
from typing import List

from application.assemblers.creative_execution_setup_assembler import CreativeExecutionSetupAssembler
from application.dtos.creative_execution_setup.creative_execution_setup_response_dto import CreativeExecutionSetupDto
from application.mappers.creative_execution_setup_mapper import CreativeExecutionSetupMapper
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose
from domain.models.creative_execution_setup.creative_execution_setup import CreativeExecutionSetup
from infrastructure.logging.logger import Logger
from infrastructure.repositories.creative_execution_setup_repository import CreativeExecutionSetupRepository


class CreativeExecutionSetupService:
    def __init__(self, logger: Logger, creative_execution_setup_repository: CreativeExecutionSetupRepository, creative_execution_setup_assembler: CreativeExecutionSetupAssembler):
        self.logger = logger
        self.repository = creative_execution_setup_repository
        self.assembler = creative_execution_setup_assembler

    def create(self, item: CreativeExecutionSetup) -> CreativeExecutionSetupDto:
        return self.get_creative_execution_setup_details_by_id(
            self.repository.create(item).id
        )

    def get_by_id(self, id: int) -> CreativeExecutionSetupDto:
        return self.get_creative_execution_setup_details_by_id(id)

    def get_creative_execution_setup_details_by_id(
        self,
        creative_execution_setup_id: int,
    ) -> CreativeExecutionSetupDto:
        item = self.repository.get_by_id(creative_execution_setup_id)
        if item is None:
            raise ValueError(
                f"Creative Execution Setup {creative_execution_setup_id} not found"
            )
        return self.assembler.assemble_dto(CreativeExecutionSetupMapper.to_dto(item))

    def list_for_ad_setup(self, ad_setup_id: int) -> List[CreativeExecutionSetupDto]:
        return [
            CreativeExecutionSetupMapper.to_dto(item)
            for item in self.repository.get_by_ad_setup_id(ad_setup_id)
        ]

    def build_llm_context(self, id: int) -> str:
        payload = json.dumps(
            self.get_creative_execution_setup_details_by_id(id).to_content_dict(),
            ensure_ascii=False,
            indent=2,
        )
        return build_llm_section("creative-execution-setup", payload, purpose=ContextSectionPurpose.CREATIVE_EXECUTION_SETUP.value)

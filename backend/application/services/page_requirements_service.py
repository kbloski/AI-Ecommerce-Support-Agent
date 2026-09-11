import json

from typing import List

from infrastructure.logging.logger import Logger
from domain.models.page_requirements.page_requirements import PageRequirements
from domain.enums.context_section_purpose import ContextSectionPurpose
from application.dtos.page_requirements.page_requirements_dto import PageRequirementsDto
from infrastructure.repositories.page_requirements_repository import PageRequirementsRepository
from application.mappers.page_requirements_mapper import PageRequirementsMapper
from application.assemblers.page_requirements_assembler import PageRequirementsAssembler
from application.services.llm_context_builder import build_llm_section
from application.services.page_sections_service import PageSectionsService


class PageRequirementsService:

    def __init__(
        self,
        logger: Logger,
        page_requirements_repository: PageRequirementsRepository,
        page_requirements_assembler: PageRequirementsAssembler,
        page_sections_service: PageSectionsService,
    ):
        self.logger = logger
        self.page_requirements_repository = page_requirements_repository
        self.page_requirements_assembler = page_requirements_assembler
        self.page_sections_service = page_sections_service

    def create_page_requirements(self, page_requirements: PageRequirements) -> PageRequirementsDto:
        created = self.page_requirements_repository.create(page_requirements)
        return self.get_page_requirements_details_by_id(page_requirements_id=created.id)

    def get_page_requirements_by_id(self, id: int) -> PageRequirementsDto:
        return self.get_page_requirements_details_by_id(page_requirements_id=id)

    def get_page_requirements_details_by_id(
        self,
        page_requirements_id: int,
    ) -> PageRequirementsDto:
        """Return Page Requirements assembled with its section requirements."""
        page_requirements_db = self.page_requirements_repository.get_by_id(
            id=page_requirements_id
        )

        if not page_requirements_db:
            raise ValueError(
                f"Page requirements {page_requirements_id} not found"
            )

        page_requirements_dto = PageRequirementsMapper.to_dto(page_requirements_db)
        return self.page_requirements_assembler.assemble_dto(page_requirements_dto)

    def get_page_requirements_by_page_strategy(self, page_strategy_id: int) -> List[PageRequirementsDto]:
        items = self.page_requirements_repository.get_by_page_strategy_id(page_strategy_id)
        dtos = [PageRequirementsMapper.to_dto(item) for item in items]
        return [self.page_requirements_assembler.assemble_dto(dto) for dto in dtos]

    def build_llm_context(self, page_requirements_id: int) -> str:
        assembled_page_requirements = self.get_page_requirements_details_by_id(
            page_requirements_id=page_requirements_id
        )

        page_requirements_content = assembled_page_requirements.to_content_dict()
        sections_by_id = {
            section["id"]: section
            for section in self.page_sections_service.get_all()
        }
        page_requirements_content["page_section_requirements"] = [
            {
                "page_section": sections_by_id.get(
                    requirement.page_section_type_id,
                    {"id": requirement.page_section_type_id},
                ),
                "requirement_type": requirement.requirement_type,
                "position": requirement.position,
            }
            for requirement in assembled_page_requirements.page_section_requirements
            if requirement.requirement_type != "excluded"
        ]

        page_requirements_json = json.dumps(
            page_requirements_content,
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section(
            "page-requirements",
            page_requirements_json,
            purpose=ContextSectionPurpose.PAGE_REQUIREMENTS.value,
        )

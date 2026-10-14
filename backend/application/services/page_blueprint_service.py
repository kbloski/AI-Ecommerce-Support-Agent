import json

from typing import List

from infrastructure.logging.logger import Logger
from domain.models.page.page_blueprint import PageBlueprint
from application.dtos.page_blueprint.page_blueprint_response_dto import PageBlueprintDto
from infrastructure.repositories.page_blueprint_repository import PageBlueprintRepository
from application.mappers.page_blueprint_mapper import PageBlueprintMapper
from application.assemblers.page_blueprint_assembler import PageBlueprintAssembler
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class PageBlueprintService:

    def __init__(
        self,
        logger: Logger,
        page_blueprint_repository: PageBlueprintRepository,
        page_blueprint_assembler: PageBlueprintAssembler,
    ):
        self.logger = logger
        self.page_blueprint_repository = page_blueprint_repository
        self.page_blueprint_assembler = page_blueprint_assembler

    def create_page_blueprint(self, page_blueprint: PageBlueprint) -> PageBlueprintDto:
        created = self.page_blueprint_repository.create(page_blueprint)
        return self.get_page_blueprint_by_id(id=created.id)

    def get_page_blueprint_by_id(self, id: int) -> PageBlueprintDto:
        page_blueprint_db = self.page_blueprint_repository.get_by_id(id)

        if not page_blueprint_db:
            raise ValueError(f"Page blueprint {id} not found")

        page_blueprint_dto = PageBlueprintMapper.to_dto(page_blueprint_db)
        return self.page_blueprint_assembler.assemble_dto(page_blueprint_dto)

    def get_page_blueprints_by_page_requirements(self, page_requirements_id: int) -> List[PageBlueprintDto]:
        items = self.page_blueprint_repository.get_by_page_requirements_id(page_requirements_id)
        dtos = [PageBlueprintMapper.to_dto(item) for item in items]
        return [self.page_blueprint_assembler.assemble_dto(dto) for dto in dtos]

    def build_llm_context(self, page_blueprint_id: int) -> str:
        page_blueprint_json = json.dumps(
            self.get_page_blueprint_by_id(id=page_blueprint_id).to_content_dict(),
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section(
            "page-blueprint",
            page_blueprint_json,
            purpose=ContextSectionPurpose.PAGE_BLUEPRINT.value,
        )

import json

from typing import List, Set

from infrastructure.logging.logger import Logger
from infrastructure.repositories.page_sections_repository import PageSectionsRepository
from infrastructure.repositories.page_section_requirements_repository import PageSectionRequirementsRepository
from application.services.llm_context_builder import build_llm_section


class PageSectionsService:
    def __init__(
        self,
        logger: Logger,
        page_sections_repository: PageSectionsRepository,
        page_section_requirements_repository: PageSectionRequirementsRepository,
    ):
        self.logger = logger
        self.page_sections_repository = page_sections_repository
        self.page_section_requirements_repository = page_section_requirements_repository

    def get_all(self) -> List[dict]:
        return self.page_sections_repository.get_all()

    def get_allowed_ids(self) -> Set[str]:
        return {section["id"] for section in self.get_all()}

    def build_llm_context_for_requirements(self, page_requirements_id: int) -> str:
        section_requirements = self.page_section_requirements_repository.find_for_page_requirements(
            page_requirements_id=page_requirements_id
        )

        sections = []
        for item in section_requirements:
            if item.requirement_type == "excluded":
                continue

            section = self.page_sections_repository.get_by_id(item.page_section_type_id)

            if section is None:
                continue

            sections.append(section)

        page_sections_json = json.dumps(
            sections,
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section("page-section-types", page_sections_json)

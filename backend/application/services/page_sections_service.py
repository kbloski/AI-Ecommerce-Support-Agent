
from typing import List, Set

from infrastructure.logging.logger import Logger
from infrastructure.repositories.page_sections_repository import PageSectionsRepository


class PageSectionsService:
    def __init__(
        self,
        logger: Logger,
        page_sections_repository: PageSectionsRepository,
    ):
        self.logger = logger
        self.page_sections_repository = page_sections_repository

    def get_all(self) -> List[dict]:
        return self.page_sections_repository.get_all()

    def get_all_for_blueprints(self) -> List[dict]:
        return [
            self._project_section(section, "selection")
            for section in self.get_all()
        ]

    def get_allowed_ids(self) -> Set[str]:
        return {section["id"] for section in self.get_all()}


    @staticmethod
    def _project_section(section: dict, guidance_stage: str) -> dict:
        projected = {
            "id": section["id"],
            "name": section["name"],
            "description": section["description"],
        }

        guidance = section.get("guidance", {})
        projected["guidance"] = {
            "shared_rules": guidance.get("shared_rules", []),
            guidance_stage: guidance.get(guidance_stage, {"rules": []}),
        }
        return projected

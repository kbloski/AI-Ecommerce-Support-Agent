from sqlalchemy.orm import Session
from typing import List, Optional

from domain.models.page_requirements.page_section_requirement import PageSectionRequirement
from infrastructure.logging.logger import Logger


class PageSectionRequirementsRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    def create_many(self, items: List[PageSectionRequirement]) -> List[PageSectionRequirement]:
        if not items:
            return []

        self.db.add_all(items)
        self.db.flush()

        for item in items:
            self.db.refresh(item)

        return items

    def find_for_page_requirements(self, page_requirements_id: int) -> List[PageSectionRequirement]:
        return (
            self.db.query(PageSectionRequirement)
            .filter(PageSectionRequirement.page_requirements_id == page_requirements_id)
            .all()
        )

    def get_by_id(self, id: int) -> Optional[PageSectionRequirement]:
        return self.db.query(PageSectionRequirement).filter(PageSectionRequirement.id == id).first()

    def delete(self, id: int) -> bool:
        item = self.db.query(PageSectionRequirement).filter(PageSectionRequirement.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

    def replace_for_page_requirements(
        self,
        page_requirements_id: int,
        items: List[PageSectionRequirement],
    ) -> List[PageSectionRequirement]:
        existing_items = self.find_for_page_requirements(page_requirements_id=page_requirements_id)

        for existing_item in existing_items:
            self.db.delete(existing_item)
        self.db.flush()

        return self.create_many(items)

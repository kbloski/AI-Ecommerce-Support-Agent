from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.page.page_blueprint import PageBlueprint
from infrastructure.logging.logger import Logger


class PageBlueprintRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    # ➕ CREATE
    def create(self, item: PageBlueprint) -> PageBlueprint:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[PageBlueprint]:
        return self.db.query(PageBlueprint).filter(PageBlueprint.id == id).first()

    # 🔍 GET BY PAGE REQUIREMENTS ID
    def get_by_page_requirements_id(self, page_requirements_id: int) -> List[PageBlueprint]:
        return (
            self.db.query(PageBlueprint)
            .filter(PageBlueprint.page_requirements_id == page_requirements_id)
            .all()
        )

    def update(self, item: PageBlueprint) -> PageBlueprint:
        existing_item = self.db.query(PageBlueprint).filter(PageBlueprint.id == item.id).first()

        if not existing_item:
            raise ValueError(f"PageBlueprint with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.commit()
        self.db.refresh(existing_item)

        return existing_item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(PageBlueprint).filter(PageBlueprint.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

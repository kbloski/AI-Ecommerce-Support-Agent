from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from domain.models.checklist.checklist_item import ChecklistItem
from infrastructure.logging.logger import Logger

class ChecklistItemsRepository:
    def __init__(self, logger : Logger, db: Session):
        self.logger=logger
        self.db = db

    def create_many(
        self,
        items: list[ChecklistItem]
    ) -> list[ChecklistItem]:

        if not items:
            return []

        self.db.add_all(items)
        self.db.commit()

        for insight in items:
            self.db.refresh(insight)

        return items

    # 🔍 GET BY ID
    def find_for_checklist(
        self,
        checklist_id: int,
    ) -> list[ChecklistItem]:

        filters = []

        if checklist_id is not None:
            filters.append(
                ChecklistItem.checklist_id == checklist_id
            )

        if not filters:
            return []

        return self.db.query(ChecklistItem).filter(
            or_(*filters)
        ).all()

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[ChecklistItem]:
        return self.db.query(ChecklistItem).filter(ChecklistItem.id == id).first()

    def update(self, item: ChecklistItem) -> ChecklistItem:
        self.db.commit()
        self.db.refresh(item)
        return item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        checklist_item = self.db.query(ChecklistItem).filter(ChecklistItem.id == id).first()

        if not checklist_item:
            return False

        self.db.delete(checklist_item)
        self.db.commit()
        return True

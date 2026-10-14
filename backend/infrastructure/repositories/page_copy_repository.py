from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.page.page_copy import PageCopy
from infrastructure.logging.logger import Logger


class PageCopyRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    # ➕ CREATE
    def create(self, item: PageCopy) -> PageCopy:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[PageCopy]:
        return self.db.query(PageCopy).filter(PageCopy.id == id).first()

    # 🔍 GET BY PAGE CONTENT PLAN ID
    def get_by_page_content_plan_id(self, page_content_plan_id: int) -> List[PageCopy]:
        return (
            self.db.query(PageCopy)
            .filter(PageCopy.page_content_plan_id == page_content_plan_id)
            .all()
        )

    def update(self, item: PageCopy) -> PageCopy:
        existing_item = self.db.query(PageCopy).filter(PageCopy.id == item.id).first()

        if not existing_item:
            raise ValueError(f"PageCopy with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.commit()
        self.db.refresh(existing_item)

        return existing_item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(PageCopy).filter(PageCopy.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

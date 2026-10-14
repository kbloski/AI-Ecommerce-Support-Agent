from sqlalchemy.orm import Session
from typing import List, Optional

from domain.models.page.page_requirements import PageRequirements
from infrastructure.logging.logger import Logger


class PageRequirementsRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    def create(self, item: PageRequirements) -> PageRequirements:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_by_id(self, id: int) -> Optional[PageRequirements]:
        return self.db.query(PageRequirements).filter(PageRequirements.id == id).first()

    def get_by_page_strategy_id(self, page_strategy_id: int) -> List[PageRequirements]:
        return (
            self.db.query(PageRequirements)
            .filter(PageRequirements.page_strategy_id == page_strategy_id)
            .all()
        )

    def update(self, item: PageRequirements) -> PageRequirements:
        existing_item = self.db.query(PageRequirements).filter(PageRequirements.id == item.id).first()

        if not existing_item:
            raise ValueError(f"PageRequirements with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.commit()
        self.db.refresh(existing_item)
        return existing_item

    def delete(self, id: int) -> bool:
        item = self.db.query(PageRequirements).filter(PageRequirements.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.page.page_strategy import PageStrategy
from infrastructure.logging.logger import Logger


class PageStrategyRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    # ➕ CREATE
    def create(self, item: PageStrategy) -> PageStrategy:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[PageStrategy]:
        return self.db.query(PageStrategy).filter(PageStrategy.id == id).first()

    # 🔍 GET BY MESSAGE STRATEGY ID
    def get_by_message_strategy_id(self, message_strategy_id: int) -> List[PageStrategy]:
        return (
            self.db.query(PageStrategy)
            .filter(PageStrategy.message_strategy_id == message_strategy_id)
            .all()
        )

    def update(self, item: PageStrategy) -> PageStrategy:
        existing_item = self.db.query(PageStrategy).filter(PageStrategy.id == item.id).first()

        if not existing_item:
            raise ValueError(f"PageStrategy with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.commit()
        self.db.refresh(existing_item)

        return existing_item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(PageStrategy).filter(PageStrategy.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

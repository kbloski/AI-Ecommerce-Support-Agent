from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.ad_setup.ad_setup import AdSetup
from infrastructure.logging.logger import Logger


class AdSetupRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    # ➕ CREATE
    def create(self, item: AdSetup) -> AdSetup:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[AdSetup]:
        return self.db.query(AdSetup).filter(AdSetup.id == id).first()

    # 🔍 GET BY CREATIVE STRATEGY ID
    def get_by_creative_strategy_id(self, creative_strategy_id: int) -> List[AdSetup]:
        return (
            self.db.query(AdSetup)
            .filter(AdSetup.creative_strategy_id == creative_strategy_id)
            .all()
        )

    def update(self, item: AdSetup) -> AdSetup:
        existing_item = self.db.query(AdSetup).filter(AdSetup.id == item.id).first()

        if not existing_item:
            raise ValueError(f"AdSetup with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.commit()
        self.db.refresh(existing_item)

        return existing_item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(AdSetup).filter(AdSetup.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

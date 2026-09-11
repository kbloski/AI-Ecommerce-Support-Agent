from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.ugc_creatives.ugc_creative import UgcCreative
from infrastructure.logging.logger import Logger


class UgcCreativeRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    # ➕ CREATE
    def create(self, item: UgcCreative) -> UgcCreative:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[UgcCreative]:
        return self.db.query(UgcCreative).filter(UgcCreative.id == id).first()

    # 🔍 GET BY MESSAGE STRATEGY ID
    def get_by_message_strategy_id(self, message_strategy_id: int) -> List[UgcCreative]:
        return (
            self.db.query(UgcCreative)
            .filter(UgcCreative.message_strategy_id == message_strategy_id)
            .all()
        )

    def update(self, item: UgcCreative) -> UgcCreative:
        self.db.commit()
        self.db.refresh(item)
        return item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(UgcCreative).filter(UgcCreative.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

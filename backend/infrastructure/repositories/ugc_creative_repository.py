from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.creative.ugc_creative import UgcCreative
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
    def get_by_offer_profile_id(self, offer_profile_id: int) -> List[UgcCreative]:
        return (
            self.db.query(UgcCreative)
            .filter(UgcCreative.offer_profile_id == offer_profile_id)
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

    def create_many(self, items):
        try:
            self.db.add_all(items)
            self.db.commit()
            for item in items:
                self.db.refresh(item)
            return items
        except Exception:
            self.db.rollback()
            raise

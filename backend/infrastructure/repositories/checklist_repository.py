from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from domain.models.checklist.checklist import Checklist
from infrastructure.logging.logger import Logger

class ChecklistRepository:
    def __init__(self, logger : Logger, db: Session):
        self.db = db

    # ➕ CREATE
    def create(self, item : Checklist) -> Checklist:
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[Checklist]:
        return self.db.query(Checklist).filter(Checklist.id == id).first()

    # 🔍 GET BY IDS
    def get_by_ids(self, ids: List[int]) -> List[Checklist]:
        return (
            self.db.query(Checklist)
            .filter(Checklist.id.in_(ids))
            .all()
        )

    def find_for_offer_profile(self, offer_profile_id: int) -> List[Checklist]:
        return (
            self.db.query(Checklist)
            .filter(Checklist.offer_profile_id == offer_profile_id)
            .order_by(Checklist.created_at.desc(), Checklist.id.desc())
            .all()
        )

    def update(self, item: Checklist) -> Checklist:
        self.db.commit()
        self.db.refresh(item)
        return item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(Checklist).filter(Checklist.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

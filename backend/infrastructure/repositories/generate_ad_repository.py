from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.generate_ad.generate_ad import GenerateAd
from infrastructure.logging.logger import Logger


class GenerateAdRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    # ➕ CREATE
    def create(self, item: GenerateAd) -> GenerateAd:
        try:
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception:
            self.db.rollback()
            raise

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[GenerateAd]:
        return self.db.query(GenerateAd).filter(GenerateAd.id == id).first()

    def get_all(self) -> List[GenerateAd]:
        return (
            self.db.query(GenerateAd)
            .order_by(GenerateAd.created_at.desc(), GenerateAd.id.desc())
            .all()
        )

    # 🔍 GET BY AD SETUP ID
    def get_by_creative_execution_setup_id(self, creative_execution_setup_id: int) -> List[GenerateAd]:
        return (
            self.db.query(GenerateAd)
            .filter(GenerateAd.creative_execution_setup_id == creative_execution_setup_id)
            .all()
        )

    def update(self, item: GenerateAd) -> GenerateAd:
        existing_item = self.db.query(GenerateAd).filter(GenerateAd.id == item.id).first()

        if not existing_item:
            raise ValueError(f"GenerateAd with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.commit()
        self.db.refresh(existing_item)

        return existing_item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(GenerateAd).filter(GenerateAd.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

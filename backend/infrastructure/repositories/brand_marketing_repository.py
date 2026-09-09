from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.brand_marketing.brand_marketing import BrandMarketing
from infrastructure.logging.logger import Logger


class BrandMarketingRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    # ➕ CREATE
    def create(self, item: BrandMarketing) -> BrandMarketing:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[BrandMarketing]:
        return self.db.query(BrandMarketing).filter(BrandMarketing.id == id).first()

    # 🔍 GET BY OFFER_PROFILE ID
    def get_by_offer_profile_id(self, offer_profile_id: int) -> List[BrandMarketing]:
        return (
            self.db.query(BrandMarketing)
            .filter(BrandMarketing.offer_profile_id == offer_profile_id)
            .all()
        )

    def update(self, item: BrandMarketing) -> BrandMarketing:
        existing_item = self.db.query(BrandMarketing).filter(BrandMarketing.id == item.id).first()

        if not existing_item:
            raise ValueError(f"BrandMarketing with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.commit()
        self.db.refresh(existing_item)

        return existing_item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(BrandMarketing).filter(BrandMarketing.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

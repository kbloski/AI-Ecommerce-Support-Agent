from sqlalchemy import case, func
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from domain.models.audience.target_audience import TargetAudience
from infrastructure.logging.logger import Logger
from common.results.paginated_result import PaginatedResult

class TargetAudiencesRepository:
    def __init__(self, logger : Logger, db: Session):
        self.logger=logger
        self.db = db

    def create_many(
        self,
        items: list[TargetAudience]
    ) -> list[TargetAudience]:

        if not items:
            return []

        self.db.add_all(items)
        self.db.commit()

        for insight in items:
            self.db.refresh(insight)

        return items

    # 🔍 GET BY ID
    def find_by_id(
        self,
        id: int ,
    ) -> TargetAudience:

        return self.db.query(TargetAudience).filter(
            TargetAudience.id == id
        ).first()



    # 🔍 GET BY ID
    def find_for_offer_profile(
        self,
        offer_profile_id: int = None,
    ) -> list[TargetAudience]:

        if offer_profile_id is None:
            return []

        return (
            self.db.query(TargetAudience)
            .filter(TargetAudience.offer_profile_id == offer_profile_id)
            .order_by(
                case((TargetAudience.review_status == "pending", 0), else_=1),
                TargetAudience.created_at.desc(),
                TargetAudience.id.desc(),
            )
            .all()
        )

    def update(self, item: TargetAudience) -> TargetAudience:
        existing_item = self.db.query(TargetAudience).filter(TargetAudience.id == item.id).first()

        if not existing_item:
            raise ValueError(f"TargetAudience with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.commit()
        self.db.refresh(existing_item)

        return existing_item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(TargetAudience).filter(TargetAudience.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True


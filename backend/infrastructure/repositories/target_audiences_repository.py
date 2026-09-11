from typing import Literal

from sqlalchemy import func
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
                TargetAudience.is_reviewed.asc(),
                TargetAudience.created_at.desc(),
                TargetAudience.id.desc(),
            )
            .all()
        )

    def search_for_offer_profile(
        self,
        offer_profile_id: int,
        page: int = 1,
        page_size: int = 20,
        is_reviewed: bool | None = None,
        sort: Literal["unreviewed_first", "reviewed_first"] = "unreviewed_first",
    ) -> PaginatedResult[TargetAudience]:
        page = max(1, page)
        page_size = max(1, page_size)

        query = self.db.query(TargetAudience).filter(
            TargetAudience.offer_profile_id == offer_profile_id
        )

        if is_reviewed is not None:
            query = query.filter(TargetAudience.is_reviewed == is_reviewed)

        review_order = (
            TargetAudience.is_reviewed.asc()
            if sort == "unreviewed_first"
            else TargetAudience.is_reviewed.desc()
        )
        total_items = query.with_entities(func.count(TargetAudience.id)).scalar() or 0
        items = (
            query
            .order_by(review_order, TargetAudience.created_at.desc(), TargetAudience.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return PaginatedResult(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
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


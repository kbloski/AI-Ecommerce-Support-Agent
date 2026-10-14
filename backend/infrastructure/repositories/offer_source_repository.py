from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from domain.models.offer.offer_source import OfferSource
from infrastructure.logging.logger import Logger
from common.results.paginated_result import PaginatedResult

class OfferSourceRepository:
    def __init__(self, logger : Logger, db: Session):
        self.db = db

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[OfferSource]:
        return self.db.query(OfferSource).filter(OfferSource.id == id).first()

    # 🔍 GET BY ID
    def get_by_offer_id(self, offer_id: int) -> Optional[OfferSource]:
        return self.db.query(OfferSource).filter(OfferSource.offer_id == offer_id).all()

    def update(self, item: OfferSource) -> OfferSource:
        existing_item = self.db.query(OfferSource).filter(OfferSource.id == item.id).first()

        if not existing_item:
            raise ValueError(f"OfferSource with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.commit()
        self.db.refresh(existing_item)

        return existing_item

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(OfferSource).filter(OfferSource.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

    # def search(self, page: int = 1, page_size: int = 20) -> PaginatedResult[Offer]:
    #         page = max(1, page)
    #         page_size = max(1, page_size)

    #         total_items = self.db.query(func.count(Offer.id)).scalar()

    #         items = (
    #             self.db.query(Offer)
    #             .offset((page - 1) * page_size)
    #             .limit(page_size)
    #             .all()
    #         )

    #         return PaginatedResult(
    #             items=items,
    #             page=page,
    #             page_size=page_size,
    #             total_items=total_items,
    #         )

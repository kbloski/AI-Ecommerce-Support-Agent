from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from domain.models.offers.offer_raw import OfferRaw
from infrastructure.logging.logger import Logger
from common.results.paginated_result import PaginatedResult

class OffersRepository:
    def __init__(self, logger : Logger, db: Session):
        self.db = db

    # ➕ CREATE
    def create(self, offer: OfferRaw) -> OfferRaw:
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[OfferRaw]:
        return self.db.query(OfferRaw).filter(OfferRaw.id == id).first()

    def search(self, page: int = 1, page_size: int = 20) -> PaginatedResult[OfferRaw]:
            page = max(1, page)
            page_size = max(1, page_size)

            total_items = self.db.query(func.count(OfferRaw.id)).scalar()

            items = (
                self.db.query(OfferRaw)
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

    def update(self, item: OfferRaw) -> OfferRaw:
        existing_offer = self.db.query(OfferRaw).filter(OfferRaw.id == item.id).first()

        if not existing_offer:
            raise ValueError(f"Offer with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_offer, key, value)

        self.db.commit()
        self.db.refresh(existing_offer)

        return existing_offer

    def delete_all(self) -> int:
        deleted = self.db.query(OfferRaw).delete()
        self.db.commit()
        return deleted

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        offer = self.db.query(OfferRaw).filter(OfferRaw.id == id).first()

        if not offer:
            return False

        self.db.delete(offer)
        self.db.commit()
        return True

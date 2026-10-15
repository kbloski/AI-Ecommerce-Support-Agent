from sqlalchemy.orm import Session

from domain.models.offer.marketing_angle import MarketingAngle


class MarketingAnglesRepository:
    def __init__(self, logger, db: Session):
        self.db = db

    def find_for_offer_profile(self, offer_profile_id: int) -> list[MarketingAngle]:
        return (self.db.query(MarketingAngle)
                .filter(MarketingAngle.offer_profile_id == offer_profile_id)
                .order_by(MarketingAngle.is_reviewed.asc(), MarketingAngle.id.desc()).all())

    def get_by_id(self, id: int) -> MarketingAngle | None:
        return self.db.get(MarketingAngle, id)

    def create_many(self, items: list[MarketingAngle]) -> list[MarketingAngle]:
        try:
            self.db.add_all(items)
            self.db.commit()
            for item in items:
                self.db.refresh(item)
            return items
        except Exception:
            self.db.rollback()
            raise

    def update(self, item: MarketingAngle) -> MarketingAngle:
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: MarketingAngle) -> None:
        self.db.delete(item)
        self.db.commit()

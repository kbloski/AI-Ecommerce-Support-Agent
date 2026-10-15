from sqlalchemy.orm import Session

from domain.models.ad.ad_concept import AdConcept


class AdConceptsRepository:
    def __init__(self, logger, db: Session):
        self.db = db

    def find_for_offer_profile(self, offer_profile_id: int) -> list[AdConcept]:
        return (self.db.query(AdConcept)
                .filter(AdConcept.offer_profile_id == offer_profile_id)
                .order_by(AdConcept.is_reviewed.asc(), AdConcept.id.desc()).all())

    def get_by_id(self, id: int) -> AdConcept | None:
        return self.db.get(AdConcept, id)

    def create_many(self, items: list[AdConcept]) -> list[AdConcept]:
        try:
            self.db.add_all(items)
            self.db.commit()
            for item in items:
                self.db.refresh(item)
            return items
        except Exception:
            self.db.rollback()
            raise

    def update(self, item: AdConcept) -> AdConcept:
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: AdConcept) -> None:
        self.db.delete(item)
        self.db.commit()

from sqlalchemy.orm import Session

from domain.models.offer_profiles.offer_profile_element import OfferProfileElement
from infrastructure.logging.logger import Logger


class OfferProfileElementsRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    def find_for_offer_profile(self, offer_profile_id: int) -> list[OfferProfileElement]:
        return (
            self.db.query(OfferProfileElement)
            .filter(OfferProfileElement.offer_profile_id == offer_profile_id)
            .order_by(
                OfferProfileElement.type.asc(),
                OfferProfileElement.name.asc(),
                OfferProfileElement.id.asc(),
            )
            .all()
        )

    def create(self, element: OfferProfileElement) -> OfferProfileElement:
        self.db.add(element)
        self.db.commit()
        self.db.refresh(element)
        return element

    def create(self, element: OfferProfileElement) -> OfferProfileElement:
        self.db.add(element)
        self.db.commit()
        self.db.refresh(element)
        return element

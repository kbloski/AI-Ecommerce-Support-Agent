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

    def get_by_id(self, id: int) -> OfferProfileElement | None:
        return self.db.query(OfferProfileElement).filter(OfferProfileElement.id == id).first()

    def update(self, element: OfferProfileElement) -> OfferProfileElement:
        existing_element = self.get_by_id(element.id)

        if not existing_element:
            raise ValueError(f"OfferProfileElement with id {element.id} not found")

        for key, value in element.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_element, key, value)

        self.db.commit()
        self.db.refresh(existing_element)

        return existing_element

    def delete(self, id: int) -> bool:
        element = self.get_by_id(id)

        if not element:
            return False

        self.db.delete(element)
        self.db.commit()
        return True

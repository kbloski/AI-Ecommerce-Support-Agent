from sqlalchemy.orm import Session
from typing import List, Optional

from domain.models.page.page_blueprint import PageBlueprint
from infrastructure.logging.logger import Logger


class PageBlueprintRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    def create(self, item: PageBlueprint) -> PageBlueprint:
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    def get_by_id(self, id: int) -> Optional[PageBlueprint]:
        return self.db.query(PageBlueprint).filter(PageBlueprint.id == id).first()

    def get_by_offer_profile_id(self, offer_profile_id: int) -> List[PageBlueprint]:
        return (
            self.db.query(PageBlueprint)
            .filter(PageBlueprint.offer_profile_id == offer_profile_id)
            .all()
        )

    def update(self, item: PageBlueprint) -> PageBlueprint:
        existing_item = self.db.query(PageBlueprint).filter(PageBlueprint.id == item.id).first()

        if not existing_item:
            raise ValueError(f"PageBlueprint with id {item.id} not found")

        for key, value in item.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_item, key, value)

        self.db.flush()
        self.db.refresh(existing_item)
        return existing_item

    def delete(self, id: int) -> bool:
        item = self.db.query(PageBlueprint).filter(PageBlueprint.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

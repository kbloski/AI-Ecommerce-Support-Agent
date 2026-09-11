from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.creative_execution_setup.creative_execution_setup import CreativeExecutionSetup
from infrastructure.logging.logger import Logger


class CreativeExecutionSetupRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    def create(self, item: CreativeExecutionSetup) -> CreativeExecutionSetup:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_by_id(self, id: int) -> Optional[CreativeExecutionSetup]:
        return self.db.query(CreativeExecutionSetup).filter(CreativeExecutionSetup.id == id).first()

    def get_by_ad_setup_id(self, ad_setup_id: int) -> List[CreativeExecutionSetup]:
        return self.db.query(CreativeExecutionSetup).filter(CreativeExecutionSetup.ad_setup_id == ad_setup_id).all()

    def update(self, item: CreativeExecutionSetup) -> CreativeExecutionSetup:
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, id: int) -> bool:
        item = self.get_by_id(id)
        if item is None:
            return False
        self.db.delete(item)
        self.db.commit()
        return True

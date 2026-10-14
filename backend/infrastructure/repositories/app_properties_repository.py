from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from domain.models.settings.app_properties import AppProperties
from infrastructure.logging.logger import Logger

PROPERTIES_ROW_ID = 1


class AppPropertiesRepository:
    def __init__(self, logger: Logger, db: Session):
        self.db = db

    def get(self) -> Optional[AppProperties]:
        return self.db.query(AppProperties).filter(AppProperties.id == PROPERTIES_ROW_ID).first()

    def upsert(self, fields: Dict[str, Any]) -> AppProperties:
        item = self.get()

        if item is None:
            item = AppProperties(id=PROPERTIES_ROW_ID)
            self.db.add(item)

        for key, value in fields.items():
            setattr(item, key, value)

        self.db.commit()
        self.db.refresh(item)

        return item

from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from domain.models.analysis.analysis import Analysis
from infrastructure.logging.logger import Logger
from common.results.paginated_result import PaginatedResult

class AnalysisRepository:
    def __init__(self, logger : Logger, db: Session):
        self.db = db

    # ➕ CREATE
    def create(self, item : Analysis) -> Analysis:
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[Analysis]:
        return self.db.query(Analysis).filter(Analysis.id == id).first()

    # 🔍 GET BY IDS
    def get_by_ids(self, ids: List[int]) -> List[Analysis]:
        return (
            self.db.query(Analysis)
            .filter(Analysis.id.in_(ids))
            .all()
        )

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(Analysis).filter(Analysis.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True
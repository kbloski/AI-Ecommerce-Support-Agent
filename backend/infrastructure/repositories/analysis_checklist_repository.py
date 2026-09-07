from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from domain.models.analysis.analysis_checklist import AnalysisChecklist
from infrastructure.logging.logger import Logger


class AnalysisChecklistRepository:
    def __init__(self, logger: Logger, db: Session):
        self.db = db
        self.logger = logger

    # ➕ UPSERT
    def upsert(self, item: AnalysisChecklist) -> AnalysisChecklist:
        existing = (
            self.db.query(AnalysisChecklist)
            .filter(
                and_(
                    AnalysisChecklist.analysis_id == item.analysis_id,
                    AnalysisChecklist.checklist_id == item.checklist_id,
                )
            )
            .first()
        )

        if existing:
            return existing

        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    # 🔍 GET BY ANALYSIS ID
    def find_by_analysis_id(self, analysis_id: int) -> List[AnalysisChecklist]:
        return (
            self.db.query(AnalysisChecklist)
            .filter(AnalysisChecklist.analysis_id == analysis_id)
            .all()
        )

    # 🔍 GET BY CHECKLIST ID
    def find_by_checklist_id(self, checklist_id: int) -> List[AnalysisChecklist]:
        return (
            self.db.query(AnalysisChecklist)
            .filter(AnalysisChecklist.checklist_id == checklist_id)
            .all()
        )

    # 🔍 FIND RELATION
    def find_relation(
        self,
        analysis_id: int,
        checklist_id: int,
    ) -> Optional[AnalysisChecklist]:
        return (
            self.db.query(AnalysisChecklist)
            .filter(
                and_(
                    AnalysisChecklist.analysis_id == analysis_id,
                    AnalysisChecklist.checklist_id == checklist_id,
                )
            )
            .first()
        )

    # ❌ DELETE BY CHECKLIST ID
    def delete_by_checklist_id(self, checklist_id: int) -> int:
        deleted = (
            self.db.query(AnalysisChecklist)
            .filter(AnalysisChecklist.checklist_id == checklist_id)
            .delete()
        )
        self.db.commit()
        return deleted
from sqlalchemy import func
from sqlalchemy.orm import Session
from common.results.paginated_result import PaginatedResult
from typing import List, Optional
from domain.models.analysis.analysis_questions import AnalysisQuestion
from infrastructure.logging.logger import Logger

class AnalysisQuestionsRepository:
    def __init__(self, logger : Logger, db: Session):
        self.logger=logger
        self.db = db

    # ➕ CREATE MANY
    def create_many(
        self,
        items: list[AnalysisQuestion]
    ) -> list[AnalysisQuestion]:

        if not items:
            return []

        self.db.add_all(items)
        self.db.commit()

        for item in items:
            self.db.refresh(item)

        return items

    # 🔍 FIND FOR ANALYSE
    def find_for_analyse(
        self,
        analysis_id: int,
    ) -> list[AnalysisQuestion]:

        return self.db.query(AnalysisQuestion).filter(
            AnalysisQuestion.analysis_id == analysis_id
        ).all()

    def search_for_analysis(
        self,
        analysis_id: int,
        page: int = 1,
        page_size: int = 20,
        is_reviewed: bool | None = None,
        sort: str = "unreviewed_first",
    ) -> PaginatedResult[AnalysisQuestion]:
        page = max(1, page)
        page_size = max(1, page_size)
        query = self.db.query(AnalysisQuestion).filter(AnalysisQuestion.analysis_id == analysis_id)
        if is_reviewed is not None:
            query = query.filter(AnalysisQuestion.is_reviewed == is_reviewed)

        review_order = AnalysisQuestion.is_reviewed.asc() if sort == "unreviewed_first" else AnalysisQuestion.is_reviewed.desc()
        total_items = query.with_entities(func.count(AnalysisQuestion.id)).scalar() or 0
        items = query.order_by(review_order, AnalysisQuestion.created_at.desc(), AnalysisQuestion.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return PaginatedResult(items=items, page=page, page_size=page_size, total_items=total_items)

    # 🔍 GET BY ID
    def get_by_id(self, id: int) -> Optional[AnalysisQuestion]:
        return self.db.query(AnalysisQuestion).filter(AnalysisQuestion.id == id).first()

    # ❌ DELETE
    def delete(self, id: int) -> bool:
        item = self.db.query(AnalysisQuestion).filter(AnalysisQuestion.id == id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

    # ❌ DELETE BY ANALYSIS ID
    def delete_by_analysis_id(self, analysis_id: int) -> int:
        deleted = (
            self.db.query(AnalysisQuestion)
            .filter(AnalysisQuestion.analysis_id == analysis_id)
            .delete()
        )
        self.db.commit()
        return deleted

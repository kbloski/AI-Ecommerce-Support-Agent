from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from domain.models.analysis.offer_source_analysis import OfferSourceAnalysis
from infrastructure.logging.logger import Logger


class OfferSourceAnalysisRepository:
    def __init__(self, logger: Logger, db: Session):
        self.db = db
        self.logger = logger

    # ➕ UPSERT
    def upsert(self, analysis: OfferSourceAnalysis) -> OfferSourceAnalysis:
        existing = (
            self.db.query(OfferSourceAnalysis)
            .filter(
                and_(
                    OfferSourceAnalysis.offer_source_id == analysis.offer_source_id,
                    OfferSourceAnalysis.analysis_id == analysis.analysis_id
                )
            )
            .first()
        )

        if existing:
            return existing

        self.db.add(analysis)
        self.db.flush()
        self.db.refresh(analysis)
        return analysis

    # 🔍 GET BY OFFER_SOURCE ID
    def find_by_offer_source_id(self, offer_source_id: int) -> List[OfferSourceAnalysis]:
        return (
            self.db.query(OfferSourceAnalysis)
            .filter(OfferSourceAnalysis.offer_source_id == offer_source_id)
            .all()
        )

    def find_relation(
        self,
        offer_source_id: int,
        analysis_id: int
    ) -> Optional[OfferSourceAnalysis]:
        return (
            self.db.query(OfferSourceAnalysis)
            .filter(
                and_(
                    OfferSourceAnalysis.offer_source_id == offer_source_id,
                    OfferSourceAnalysis.analysis_id == analysis_id
                )
            )
            .first()
        )

    # ❌ DELETE BY ANALYSIS ID
    def delete_by_analysis_id(self, analysis_id: int) -> int:
        deleted = (
            self.db.query(OfferSourceAnalysis)
            .filter(OfferSourceAnalysis.analysis_id == analysis_id)
            .delete()
        )
        self.db.commit()
        return deleted
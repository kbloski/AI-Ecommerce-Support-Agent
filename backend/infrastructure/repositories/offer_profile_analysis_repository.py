from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from domain.models.analysis.offer_profile_analysis import OfferProfileAnalysis
from infrastructure.logging.logger import Logger


class OfferProfileAnalysisRepository:
    def __init__(self, logger: Logger, db: Session):
        self.db = db
        self.logger = logger

    # ➕ UPSERT
    def upsert(self, analysis: OfferProfileAnalysis) -> OfferProfileAnalysis:
        existing = (
            self.db.query(OfferProfileAnalysis)
            .filter(
                and_(
                    OfferProfileAnalysis.offer_profile_id == analysis.offer_profile_id,
                    OfferProfileAnalysis.analysis_id == analysis.analysis_id
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

    # 🔍 GET BY OFFER_PROFILE ID
    def find_by_offer_profile_id(self, offer_profile_id: int) -> List[OfferProfileAnalysis]:
        return (
            self.db.query(OfferProfileAnalysis)
            .filter(OfferProfileAnalysis.offer_profile_id == offer_profile_id)
            .all()
        )

    def find_relation(
        self,
        offer_profile_id: int,
        analysis_id: int
    ) -> Optional[OfferProfileAnalysis]:
        return (
            self.db.query(OfferProfileAnalysis)
            .filter(
                and_(
                    OfferProfileAnalysis.offer_profile_id == offer_profile_id,
                    OfferProfileAnalysis.analysis_id == analysis_id
                )
            )
            .first()
        )

    # ❌ DELETE BY ANALYSIS ID
    def delete_by_analysis_id(self, analysis_id: int) -> int:
        deleted = (
            self.db.query(OfferProfileAnalysis)
            .filter(OfferProfileAnalysis.analysis_id == analysis_id)
            .delete()
        )
        self.db.commit()
        return deleted
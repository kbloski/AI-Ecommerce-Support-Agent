from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from infrastructure.database.db import Base
from domain.enums.table_name import TableName
from domain.enums.ad_formats import AdFormats


class AdConcept(Base):
    __tablename__ = TableName.AD_CONCEPTS.value
    __table_args__ = (
        CheckConstraint(
            f"format IN ('{AdFormats.VIDEO.value}', '{AdFormats.IMAGE.value}')",
            name="ck_ad_concepts_format",
        ),
        CheckConstraint("generation_mode IN ('standard', 'experimental')", name="ck_ad_concepts_generation_mode"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_profile_id = Column(Integer, ForeignKey("offer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    generation_mode = Column(String(16), nullable=False, default="standard", server_default="standard")
    marketing_angles = relationship("MarketingAngle", secondary="ad_concept_marketing_angles")
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    format = Column(String(16), nullable=False)
    core_idea = Column(Text, nullable=False)
    key_message = Column(Text, nullable=False)
    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

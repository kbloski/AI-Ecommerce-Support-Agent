from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from domain.enums.table_name import TableName
from domain.enums.ad_formats import AdFormats


class AdCreativePlan(Base):
    __tablename__ = TableName.AD_CREATIVE_PLANS.value
    __table_args__ = (
        CheckConstraint(
            "format IN (" + ", ".join(f"'{value.value}'" for value in AdFormats) + ")",
            name="ck_ad_creative_plans_format",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_profile_id = Column(Integer, ForeignKey("offer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    ad_concept_id = Column(Integer, ForeignKey("ad_concepts.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    format = Column(String(64), nullable=False)
    plan = Column(Text, nullable=False)
    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

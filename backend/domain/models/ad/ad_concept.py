from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class AdConcept(Base):
    __tablename__ = TableName.AD_CONCEPTS.value
    __table_args__ = (CheckConstraint("format IN ('video', 'image')", name="ck_ad_concepts_format"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_profile_id = Column(Integer, ForeignKey("offer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    marketing_angle_id = Column(Integer, ForeignKey("marketing_angles.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    format = Column(String(16), nullable=False)
    core_idea = Column(Text, nullable=False)
    key_message = Column(Text, nullable=False)
    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

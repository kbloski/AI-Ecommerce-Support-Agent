from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class MarketingAngle(Base):
    __tablename__ = TableName.MARKETING_ANGLES.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_profile_id = Column(Integer, ForeignKey("offer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    core_message = Column(Text, nullable=False, default="", server_default="")
    value_proposition = Column(Text, nullable=False, default="", server_default="")
    pain_point = Column(Text, nullable=False, default="", server_default="")
    desire = Column(Text, nullable=False, default="", server_default="")
    emotional_driver = Column(Text, nullable=False, default="", server_default="")
    supporting_arguments = Column(JSON, nullable=False, default=list, server_default="[]")
    proof_points = Column(JSON, nullable=False, default=list, server_default="[]")
    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

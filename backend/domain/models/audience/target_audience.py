from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Index, JSON, Boolean
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class TargetAudience(Base, JSONSerializable):
    __tablename__ = TableName.TARGET_AUDIENCES.value

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relation
    offer_profile_id = Column(
        Integer,
        ForeignKey(TableName.OFFER_PROFILES + ".id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Status
    fact_status = Column(String(20), nullable=False, index=True)
    review_status = Column(String(20), nullable=False, default="pending", server_default="pending", index=True)

    # Basic information
    name = Column(String(255), nullable=False)
    reason = Column(String, nullable=True)

    # AI evaluation
    score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)

    # Demographics
    age_min = Column(Integer, nullable=True)
    age_max = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    purchasing_power = Column(String(100), nullable=True)

    # Psychographics
    lifestyles = Column(JSON, nullable=True)
    values = Column(JSON, nullable=True)

    # Buying behavior
    awareness_level = Column(String(50), nullable=True)
    price_sensitivity = Column(String(50), nullable=True)
    research_level = Column(String(50), nullable=True)
    decision_time = Column(String(100), nullable=True)

    # Customer insights
    pain_points = Column(JSON, nullable=True)
    motivations = Column(JSON, nullable=True)
    buying_triggers = Column(JSON, nullable=True)
    objections = Column(JSON, nullable=True)

    # Marketing
    message_angles = Column(JSON, nullable=True)
    marketing_channels = Column(JSON, nullable=True)

    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "ix_target_audience_offer_profile_fact_status",
            "offer_profile_id",
            "fact_status"
        ),
        Index(
            "ix_target_audience_score",
            "score"
        ),
        Index(
            "ix_target_audience_gender",
            "gender"
        ),
    )

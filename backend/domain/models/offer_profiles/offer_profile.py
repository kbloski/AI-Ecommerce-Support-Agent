from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class OfferProfile(Base, JSONSerializable):
    __tablename__ = TableName.OFFER_PROFILES.value

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Related offer
    offer_id = Column(
        Integer,
        ForeignKey(TableName.OFFERS_RAW+".id", ondelete="CASCADE"),
        nullable=False,
    )

    # AI-generated offer_profile
    offer_summary = Column(Text, nullable=True)
    category = Column(Text, nullable=True)

    value_proposition=Column(Text, nullable=True)

    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

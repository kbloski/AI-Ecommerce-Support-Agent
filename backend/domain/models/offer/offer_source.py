from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class OfferSource(Base, JSONSerializable):
    __tablename__ = TableName.OFFER_SOURCES.value

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Related offer
    offer_id = Column(
        Integer,
        ForeignKey(TableName.OFFERS_RAW+".id", ondelete="CASCADE"),
        nullable=False,
    )

    # AI-extracted, complete factual record of the offer
    offer_details = Column(Text, nullable=True)


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

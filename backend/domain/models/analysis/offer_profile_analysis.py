from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func

from common.mixins.json_serializable import JSONSerializable
from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class OfferProfileAnalysis(Base, JSONSerializable):
    __tablename__ = TableName.OFFER_PROFILE_ANALYSIS.value

    offer_profile_id = Column(
        Integer,
        ForeignKey(TableName.OFFER_PROFILES + ".id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    )

    analysis_id = Column(
        Integer,
        ForeignKey(TableName.ANALYSIS + ".id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    )

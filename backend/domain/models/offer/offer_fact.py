from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName
from infrastructure.database.db import Base


class OfferFact(Base, JSONSerializable):
    __tablename__ = TableName.OFFER_FACTS.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_source_id = Column(Integer, ForeignKey(TableName.OFFER_SOURCES.value + ".id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

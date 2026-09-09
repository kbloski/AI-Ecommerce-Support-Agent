from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName
from infrastructure.database.db import Base


class OfferRaw(Base, JSONSerializable):
    __tablename__ = TableName.OFFERS_RAW.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

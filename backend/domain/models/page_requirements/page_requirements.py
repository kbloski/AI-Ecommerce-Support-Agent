from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class PageRequirements(Base, JSONSerializable):

    __tablename__ = TableName.PAGE_REQUIREMENTS.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    page_strategy_id = Column(
        Integer,
        ForeignKey(TableName.PAGE_STRATEGY + ".id", ondelete="CASCADE"),
        nullable=False
    )

    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

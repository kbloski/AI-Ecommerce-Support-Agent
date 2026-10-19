from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class PageBlueprint(Base, JSONSerializable):

    __tablename__ = TableName.PAGE_BLUEPRINT.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False, default="", server_default="")

    offer_profile_id = Column(
        Integer,
        ForeignKey(TableName.OFFER_PROFILES + ".id", ondelete="CASCADE"),
        nullable=False
    )

    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

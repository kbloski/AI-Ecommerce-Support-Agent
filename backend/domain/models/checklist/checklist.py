from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func

from common.mixins.json_serializable import JSONSerializable
from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class Checklist(Base, JSONSerializable):
    __tablename__ = TableName.CHECKLIST.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_profile_id = Column(
        Integer,
        ForeignKey(f"{TableName.OFFER_PROFILES}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)

    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

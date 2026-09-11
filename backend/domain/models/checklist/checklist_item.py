from sqlalchemy import Boolean, Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from common.mixins.json_serializable import JSONSerializable
from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class ChecklistItem(Base, JSONSerializable):
    __tablename__ = TableName.CHECKLIST_ITEM.value

    id = Column(Integer, primary_key=True, autoincrement=True)

    checklist_id = Column(
        Integer,
        ForeignKey(f"{TableName.CHECKLIST.value}.id"),
        nullable=False
    )

    title = Column(Text, nullable=False)
    description= Column(Text, nullable=True)
    note = Column(Text, nullable=True)
    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0", index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

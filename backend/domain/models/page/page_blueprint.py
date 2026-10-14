from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class PageBlueprint(Base, JSONSerializable):

    __tablename__ = TableName.PAGE_BLUEPRINT.value

    # primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    page_strategy_id = Column(
        Integer,
        ForeignKey(TableName.PAGE_STRATEGY + ".id", ondelete="CASCADE"),
        nullable=False
    )

    page_requirements_id = Column(
        Integer,
        ForeignKey(TableName.PAGE_REQUIREMENTS + ".id", ondelete="CASCADE"),
        nullable=True
    )

    page_type = Column(String, nullable=True)
    primary_conversion_goal = Column(String, nullable=True)

    sections = Column(JSON, nullable=True)

    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")

    # timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

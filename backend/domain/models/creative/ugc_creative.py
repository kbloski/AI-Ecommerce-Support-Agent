from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class UgcCreative(Base, JSONSerializable):

    __tablename__ = TableName.UGC_CREATIVES.value

    # primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # relations
    message_strategy_id = Column(
        Integer,
        ForeignKey(TableName.MESSAGE_STRATEGY + ".id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=True)
    customer_persona = Column(JSON, nullable=True)
    content_format = Column(String, nullable=True)
    angle = Column(String, nullable=True)
    hook_idea = Column(String, nullable=True)
    video_flow = Column(JSON, nullable=True)
    recording_style = Column(String, nullable=True)
    platform_fit = Column(JSON, nullable=True)
    cta = Column(String, nullable=True)
    why_it_should_work = Column(String, nullable=True)

    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")
    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0")

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

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName
from infrastructure.database.db import Base


class CreativeExecutionSetup(Base, JSONSerializable):
    __tablename__ = TableName.CREATIVE_EXECUTION_SETUPS.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_setup_id = Column(Integer, ForeignKey(TableName.AD_SETUP + ".id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    number_of_slides = Column(Integer, nullable=True)
    ad_framework_id = Column(String, nullable=True)
    creative_angle_id = Column(String, nullable=True)
    execution_style_id = Column(String, nullable=True)
    additional_instructions = Column(Text, nullable=True)
    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

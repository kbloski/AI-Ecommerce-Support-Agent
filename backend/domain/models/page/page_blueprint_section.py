from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from domain.enums.table_name import TableName
from infrastructure.database.db import Base


class PageBlueprintSection(Base):
    __tablename__ = TableName.PAGE_BLUEPRINT_SECTIONS.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_blueprint_id = Column(Integer, ForeignKey(TableName.PAGE_BLUEPRINT.value + ".id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)
    is_optional = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

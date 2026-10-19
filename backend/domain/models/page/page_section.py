from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from domain.enums.table_name import TableName
from infrastructure.database.db import Base


class PageSection(Base):
    __tablename__ = TableName.PAGE_SECTIONS.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey(TableName.PAGES.value + ".id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

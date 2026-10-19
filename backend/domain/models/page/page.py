from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from domain.enums.table_name import TableName
from infrastructure.database.db import Base


class Page(Base):
    __tablename__ = TableName.PAGES.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_profile_id = Column(Integer, ForeignKey(TableName.OFFER_PROFILES.value + ".id", ondelete="CASCADE"), nullable=False, index=True)
    page_blueprint_id = Column(Integer, ForeignKey(TableName.PAGE_BLUEPRINT.value + ".id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="", server_default="")
    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

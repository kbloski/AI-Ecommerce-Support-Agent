from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class BrandStyle(Base):
    __tablename__ = TableName.BRAND_STYLES.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_profile_id = Column(Integer, ForeignKey(TableName.OFFER_PROFILES.value + ".id", ondelete="CASCADE"), nullable=False, index=True)
    font_family = Column(String(255), nullable=False)
    brand_color = Column(String(7), nullable=False)
    text_color = Column(String(7), nullable=False)
    background_color = Column(String(7), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

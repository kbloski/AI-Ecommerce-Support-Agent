from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func
from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class OfferProfile(Base):
    __tablename__ = TableName.OFFER_PROFILES.value
    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_source_id = Column(Integer, ForeignKey(TableName.OFFER_SOURCES.value + ".id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

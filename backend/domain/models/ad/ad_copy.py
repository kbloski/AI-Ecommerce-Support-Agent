from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class AdCopy(Base):
    __tablename__ = TableName.AD_COPIES.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_profile_id = Column(Integer, ForeignKey("offer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    primary_text = Column(Text, nullable=False)
    headline = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    cta = Column(Text, nullable=True)
    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0", index=True)

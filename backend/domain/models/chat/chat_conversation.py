from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class ChatConversation(Base):
    __tablename__ = TableName.CHAT_CONVERSATIONS.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    # Resource selection in the same shape as the resource export
    context = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

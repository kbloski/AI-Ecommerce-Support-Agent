from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class AppProperties(Base, JSONSerializable):
    """Application-wide properties stored in a single row (id=1).

    Currently includes Ollama overrides; unset fields use `.env` defaults.
    The row is created lazily on the first save.
    """

    __tablename__ = TableName.APP_PROPERTIES.value

    id = Column(Integer, primary_key=True, autoincrement=True)

    ollama_url = Column(String, nullable=True)
    ollama_model = Column(String, nullable=True)
    ollama_timeout = Column(Integer, nullable=True)
    ollama_context_length = Column(Integer, nullable=True)
    ollama_temperature = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

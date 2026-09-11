from sqlalchemy import Boolean, Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func

from common.mixins.json_serializable import JSONSerializable
from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class AnalysisQuestion(Base, JSONSerializable):
    __tablename__ = TableName.ANALYSIS_QUESTIONS.value

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    analysis_id = Column(
        Integer,
        ForeignKey(f"{TableName.ANALYSIS.value}.id", ondelete="CASCADE"),
        nullable=False
    )

    question_answer_id = Column(
        Integer,
        ForeignKey(f"{TableName.QUESTION_ANSWERS.value}.id", ondelete="CASCADE"),
        nullable=False
    )

    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0", index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

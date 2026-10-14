from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class PageSectionRequirement(Base, JSONSerializable):

    __tablename__ = TableName.PAGE_SECTION_REQUIREMENT.value

    id = Column(Integer, primary_key=True, autoincrement=True)

    page_requirements_id = Column(
        Integer,
        ForeignKey(TableName.PAGE_REQUIREMENTS + ".id", ondelete="CASCADE"),
        nullable=False
    )

    page_section_type_id = Column(String, nullable=False)
    requirement_type = Column(String, nullable=False)
    position = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

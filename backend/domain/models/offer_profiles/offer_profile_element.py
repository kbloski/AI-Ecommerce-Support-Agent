from sqlalchemy import Boolean, Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from common.mixins.json_serializable import JSONSerializable
from domain.enums.offer_profile_element_type import OfferProfileElementType
from domain.enums.table_name import TableName
from infrastructure.database.db import Base


class OfferProfileElement(Base, JSONSerializable):
    __tablename__ = TableName.OFFER_PROFILE_ELEMENTS.value

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_profile_id = Column(
        Integer,
        ForeignKey(TableName.OFFER_PROFILES.value + ".id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(
        SqlEnum(
            OfferProfileElementType,
            native_enum=False,
            values_callable=lambda values: [item.value for item in values],
        ),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_reviewed = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

from sqlalchemy import BigInteger, Column, ForeignKey, Integer
from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class OfferProfileAdditionalContext(Base):
    __tablename__ = TableName.OFFER_PROFILE_ADDITIONAL_CONTEXTS.value
    offer_profile_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey(TableName.OFFER_PROFILES.value + ".id", ondelete="CASCADE"), primary_key=True)
    additional_context_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey(TableName.ADDITIONAL_CONTEXTS.value + ".id", ondelete="CASCADE"), primary_key=True, index=True)

from sqlalchemy import BigInteger, Column, ForeignKey, Integer

from domain.enums.table_name import TableName
from infrastructure.database.db import Base


class OfferProfileNote(Base):
    __tablename__ = TableName.OFFER_PROFILE_NOTES.value

    offer_profile_id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey(TableName.OFFER_PROFILES.value + ".id", ondelete="CASCADE"),
        primary_key=True,
    )
    note_id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey(TableName.NOTES.value + ".id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

from sqlalchemy import Column, ForeignKey, Integer

from infrastructure.database.db import Base
from domain.enums.table_name import TableName


class AdConceptMarketingAngle(Base):
    __tablename__ = TableName.AD_CONCEPT_MARKETING_ANGLES.value

    ad_concept_id = Column(Integer, ForeignKey("ad_concepts.id", ondelete="CASCADE"), primary_key=True)
    marketing_angle_id = Column(Integer, ForeignKey("marketing_angles.id", ondelete="CASCADE"), primary_key=True)

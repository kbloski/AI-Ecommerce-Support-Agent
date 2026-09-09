from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class BrandMarketing(Base, JSONSerializable):

    __tablename__ = TableName.BRAND_MARKETING.value

    # primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # relation to product offer_profile
    offer_profile_id = Column(
        Integer,
        ForeignKey(TableName.OFFER_PROFILES.value+".id", ondelete="CASCADE"),
        nullable=False
    )

    # basic
    brand_name = Column(String, nullable=True)

    # positioning
    brand_positioning = Column(Text, nullable=True)
    brand_category = Column(String, nullable=True)
    brand_target_customer = Column(Text, nullable=True)
    brand_competitive_difference = Column(Text, nullable=True)

    brand_purpose = Column(Text, nullable=True)
    brand_promise = Column(Text, nullable=True)

    brand_personality = Column(JSON, nullable=True)
    brand_values = Column(JSON, nullable=True)

    brand_voice = Column(Text, nullable=True)
    brand_tone = Column(Text, nullable=True)
    brand_tone_social_media = Column(Text, nullable=True)
    brand_tone_customer_communication = Column(Text, nullable=True)

    tagline = Column(Text, nullable=True)
    unique_selling_proposition = Column(Text, nullable=True)

    key_messages = Column(JSON, nullable=True)
    target_perception = Column(JSON, nullable=True)
    target_emotions = Column(JSON, nullable=True)
    brand_associations = Column(JSON, nullable=True)

    customer_desires = Column(JSON, nullable=True)
    customer_pains = Column(JSON, nullable=True)
    customer_fears = Column(JSON, nullable=True)
    customer_objections = Column(JSON, nullable=True)
    purchase_motivators = Column(JSON, nullable=True)

    brand_story = Column(Text, nullable=True)
    brand_story_angle = Column(Text, nullable=True)
    customer_transformation = Column(Text, nullable=True)

    content_pillars = Column(JSON, nullable=True)
    storytelling_angles = Column(JSON, nullable=True)
    ugc_direction = Column(JSON, nullable=True)

    visual_style = Column(Text, nullable=True)
    visual_direction = Column(Text, nullable=True)

    brand_always_do = Column(JSON, nullable=True)
    brand_never_do = Column(JSON, nullable=True)

    is_favorite = Column(Boolean, nullable=False, default=False, server_default="0")

    # timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

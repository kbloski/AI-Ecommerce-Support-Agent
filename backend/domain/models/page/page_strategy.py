from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func

from infrastructure.database.db import Base
from common.mixins.json_serializable import JSONSerializable
from domain.enums.table_name import TableName


class PageStrategy(Base, JSONSerializable):

    __tablename__ = TableName.PAGE_STRATEGY.value

    # primary key
    id = Column(Integer, primary_key=True, autoincrement=True)


    message_strategy_id = Column(
        Integer,
        ForeignKey(TableName.MESSAGE_STRATEGY + ".id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)
    goal = Column(String, nullable=True)
    conversion_action = Column(String, nullable=True)

    target_audience = Column(String, nullable=True)
    customer_awareness_level = Column(String, nullable=True)
    customer_journey_stage = Column(String, nullable=True)

    core_value_proposition = Column(String, nullable=True)
    main_message = Column(String, nullable=True)
    message_angle = Column(String, nullable=True)

    customer_problem = Column(String, nullable=True)
    customer_desire = Column(String, nullable=True)

    emotional_drivers = Column(JSON, nullable=True)
    rational_drivers = Column(JSON, nullable=True)
    purchase_motivators = Column(JSON, nullable=True)
    purchase_barriers = Column(JSON, nullable=True)
    objections_to_resolve = Column(JSON, nullable=True)
    trust_requirements = Column(JSON, nullable=True)

    competitive_positioning = Column(String, nullable=True)
    brand_voice_direction = Column(String, nullable=True)

    conversion_strategy = Column(JSON, nullable=True)
    customer_journey_strategy = Column(JSON, nullable=True)

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

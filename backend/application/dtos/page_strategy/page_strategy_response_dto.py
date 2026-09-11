from typing import Optional, List

from common.mixins.json_serializable import JSONSerializable


class PageStrategyDto(JSONSerializable):

    def __init__(
        self,
        id: int,
        message_strategy_id: int,
        name: str,
        goal: Optional[str],
        conversion_action: Optional[str],
        target_audience: Optional[str],
        customer_awareness_level: Optional[str],
        customer_journey_stage: Optional[str],
        core_value_proposition: Optional[str],
        main_message: Optional[str],
        message_angle: Optional[str],
        customer_problem: Optional[str],
        customer_desire: Optional[str],
        emotional_drivers: Optional[List[str]],
        rational_drivers: Optional[List[str]],
        purchase_motivators: Optional[List[str]],
        purchase_barriers: Optional[List[str]],
        objections_to_resolve: Optional[List[str]],
        trust_requirements: Optional[List[str]],
        competitive_positioning: Optional[str],
        brand_voice_direction: Optional[str],
        conversion_strategy: Optional[dict],
        customer_journey_strategy: Optional[List[dict]],
    ):
        self.id = id
        self.message_strategy_id = message_strategy_id
        self.name = name
        self.goal = goal
        self.conversion_action = conversion_action
        self.target_audience = target_audience
        self.customer_awareness_level = customer_awareness_level
        self.customer_journey_stage = customer_journey_stage
        self.core_value_proposition = core_value_proposition
        self.main_message = main_message
        self.message_angle = message_angle
        self.customer_problem = customer_problem
        self.customer_desire = customer_desire
        self.emotional_drivers = emotional_drivers
        self.rational_drivers = rational_drivers
        self.purchase_motivators = purchase_motivators
        self.purchase_barriers = purchase_barriers
        self.objections_to_resolve = objections_to_resolve
        self.trust_requirements = trust_requirements
        self.competitive_positioning = competitive_positioning
        self.brand_voice_direction = brand_voice_direction
        self.conversion_strategy = conversion_strategy
        self.customer_journey_strategy = customer_journey_strategy

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "message_strategy_id": self.message_strategy_id,
            "name": self.name,
            "goal": self.goal,
            "conversion_action": self.conversion_action,
            "target_audience": self.target_audience,
            "customer_awareness_level": self.customer_awareness_level,
            "customer_journey_stage": self.customer_journey_stage,
            "core_value_proposition": self.core_value_proposition,
            "main_message": self.main_message,
            "message_angle": self.message_angle,
            "customer_problem": self.customer_problem,
            "customer_desire": self.customer_desire,
            "emotional_drivers": self.emotional_drivers,
            "rational_drivers": self.rational_drivers,
            "purchase_motivators": self.purchase_motivators,
            "purchase_barriers": self.purchase_barriers,
            "objections_to_resolve": self.objections_to_resolve,
            "trust_requirements": self.trust_requirements,
            "competitive_positioning": self.competitive_positioning,
            "brand_voice_direction": self.brand_voice_direction,
            "conversion_strategy": self.conversion_strategy,
            "customer_journey_strategy": self.customer_journey_strategy,
        }

        return {k: v for k, v in data.items() if k not in exclude}

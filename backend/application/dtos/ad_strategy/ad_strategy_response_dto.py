from typing import Optional, List

from common.mixins.json_serializable import JSONSerializable


class AdStrategyDto(JSONSerializable):

    def __init__(
        self,
        id: int,
        message_strategy_id: int,
        name: Optional[str],
        objective: Optional[dict],
        customer_stage: Optional[str],
        priority_audiences: Optional[List[dict]],
        audience_angles: Optional[List[dict]],
        message_angles: Optional[List[dict]],
        offer_angles: Optional[List[dict]],
        creative_concepts: Optional[List[dict]],
        recommended_formats: Optional[List[dict]],
        testing_hypotheses: Optional[List[dict]],
    ):
        self.id = id
        self.message_strategy_id = message_strategy_id
        self.name = name
        self.objective = objective
        self.customer_stage = customer_stage
        self.priority_audiences = priority_audiences
        self.audience_angles = audience_angles
        self.message_angles = message_angles
        self.offer_angles = offer_angles
        self.creative_concepts = creative_concepts
        self.recommended_formats = recommended_formats
        self.testing_hypotheses = testing_hypotheses

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "message_strategy_id": self.message_strategy_id,
            "name": self.name,
            "objective": self.objective,
            "customer_stage": self.customer_stage,
            "priority_audiences": self.priority_audiences,
            "audience_angles": self.audience_angles,
            "message_angles": self.message_angles,
            "offer_angles": self.offer_angles,
            "creative_concepts": self.creative_concepts,
            "recommended_formats": self.recommended_formats,
            "testing_hypotheses": self.testing_hypotheses,
        }

        return {k: v for k, v in data.items() if k not in exclude}

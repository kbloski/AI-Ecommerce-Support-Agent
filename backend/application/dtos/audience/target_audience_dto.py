from typing import List, Any

from common.mixins.json_serializable import JSONSerializable


class TargetAudienceDto(JSONSerializable):

    def __init__(
        self,
        id: int,
        offer_profile_id: int | None,
        fact_status: str,
        is_reviewed: bool,
        name: str,
        reason: str | None,
        score: float | None,
        confidence: float | None,
        age_min: int | None,
        age_max: int | None,
        gender: str | None,
        location: str | None,
        purchasing_power: str | None,
        lifestyles: List[Any] | None,
        values: List[Any] | None,
        awareness_level: str | None,
        price_sensitivity: str | None,
        research_level: str | None,
        decision_time: str | None,
        pain_points: List[Any] | None,
        motivations: List[Any] | None,
        buying_triggers: List[Any] | None,
        objections: List[Any] | None,
        message_angles: List[Any] | None,
        marketing_channels: List[Any] | None,
    ):
        self.id = id
        self.offer_profile_id = offer_profile_id
        self.fact_status = fact_status
        self.is_reviewed = is_reviewed

        self.name = name
        self.reason = reason

        self.score = score
        self.confidence = confidence

        self.age_min = age_min
        self.age_max = age_max
        self.gender = gender
        self.location = location
        self.purchasing_power = purchasing_power

        self.lifestyles = lifestyles
        self.values = values

        self.awareness_level = awareness_level
        self.price_sensitivity = price_sensitivity
        self.research_level = research_level
        self.decision_time = decision_time

        self.pain_points = pain_points
        self.motivations = motivations
        self.buying_triggers = buying_triggers
        self.objections = objections

        self.message_angles = message_angles
        self.marketing_channels = marketing_channels


    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "offer_profile_id": self.offer_profile_id,
            "fact_status": self.fact_status,
            "is_reviewed": self.is_reviewed,

            "name": self.name,
            "reason": self.reason,

            "score": self.score,
            "confidence": self.confidence,

            "age_min": self.age_min,
            "age_max": self.age_max,
            "gender": self.gender,
            "location": self.location,
            "purchasing_power": self.purchasing_power,

            "lifestyles": self.lifestyles,
            "values": self.values,

            "awareness_level": self.awareness_level,
            "price_sensitivity": self.price_sensitivity,
            "research_level": self.research_level,
            "decision_time": self.decision_time,

            "pain_points": self.pain_points,
            "motivations": self.motivations,
            "buying_triggers": self.buying_triggers,
            "objections": self.objections,

            "message_angles": self.message_angles,
            "marketing_channels": self.marketing_channels,
        }

        return {
            k: v
            for k, v in data.items()
            if k not in exclude
        }

    def to_content_dict(self):
        data = self.to_dict(exclude=["id", "offer_profile_id", "is_reviewed"])
        return data

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
        age_min: int | None,
        age_max: int | None,
        gender: str | None,
        lifestyles: List[Any] | None,
        values: List[Any] | None,
        pain_points: List[Any] | None,
        motivations: List[Any] | None,
        buying_triggers: List[Any] | None,
        desires: List[Any] | None,
    ):
        self.id = id
        self.offer_profile_id = offer_profile_id
        self.fact_status = fact_status
        self.is_reviewed = is_reviewed

        self.name = name


        self.age_min = age_min
        self.age_max = age_max
        self.gender = gender

        self.lifestyles = lifestyles
        self.values = values


        self.pain_points = pain_points
        self.motivations = motivations
        self.buying_triggers = buying_triggers
        self.desires = desires



    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "offer_profile_id": self.offer_profile_id,
            "fact_status": self.fact_status,
            "is_reviewed": self.is_reviewed,

            "name": self.name,


            "age_min": self.age_min,
            "age_max": self.age_max,
            "gender": self.gender,

            "lifestyles": self.lifestyles or [],
            "values": self.values or [],


            "pain_points": self.pain_points or [],
            "motivations": self.motivations or [],
            "buying_triggers": self.buying_triggers or [],
            "desires": self.desires or [],

        }

        return {
            k: v
            for k, v in data.items()
            if k not in exclude
        }

    def to_content_dict(self):
        data = self.to_dict(exclude=["id", "offer_profile_id", "is_reviewed", "fact_status"])
        return data

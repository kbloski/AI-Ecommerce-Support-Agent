from typing import Any, Optional, List
from ..audience.target_audience_dto import TargetAudienceDto
from common.mixins.json_serializable import JSONSerializable

class OfferProfileDto(JSONSerializable):

    target_audiences: List[TargetAudienceDto] = []
    offer_profile_elements: List[Any] = []

    def __init__(
        self,
        id: int,
        offer_id: int,
        offer_summary: Optional[str] = None,
        category: Optional[str] = None,
        value_proposition: Optional[str] = None,
    ):
        self.id = id
        self.offer_id = offer_id
        self.offer_summary = offer_summary
        self.category = category
        self.value_proposition = value_proposition

    def _sorted_offer_profile_elements(self) -> List[Any]:
        """Group elements by type (grouping = stable sort by type, then name)."""
        return sorted(
            self.offer_profile_elements,
            key=lambda element: (str(element.type), element.name),
        )

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "offer_id": self.offer_id,
            "offer_summary": self.offer_summary,
            "category": self.category,
            "value_proposition": self.value_proposition,
            "target_audiences" : [t.to_dict() for t in self.target_audiences],
            "offer_profile_elements": [e.to_dict() for e in self._sorted_offer_profile_elements()],
        }

        return {k: v for k, v in data.items() if k not in exclude}

    def to_content_dict(self):
        data = self.to_dict(exclude=["id", "offer_id"])
        data["target_audiences"] = [t.to_content_dict() for t in self.target_audiences]
        data["offer_profile_elements"] = [e.to_content_dict() for e in self._sorted_offer_profile_elements()]
        return data

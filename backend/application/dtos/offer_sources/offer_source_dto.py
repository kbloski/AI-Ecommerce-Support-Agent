from typing import Optional, List
from ..audience.target_audience_dto import TargetAudienceDto
from .offer_source_element_dto import OfferSourceElementDto
from common.mixins.json_serializable import JSONSerializable

class OfferSourceDto(JSONSerializable):

    target_audiences: List[TargetAudienceDto] = []
    offer_source_elements: List[OfferSourceElementDto] = []

    def __init__(
        self,
        id: int,
        offer_id: int,
        offer_summary: Optional[str] = None,
    ):
        self.offer_facts = []
        self.id = id
        self.offer_id = offer_id
        self.offer_summary = offer_summary

    def _sorted_offer_source_elements(self) -> List[OfferSourceElementDto]:
        """Group elements by type (grouping = stable sort by type, then name)."""
        return sorted(
            self.offer_source_elements,
            key=lambda element: (str(element.type), element.name),
        )

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "offer_id": self.offer_id,
            "offer_summary": self.offer_summary,
            "offer_facts": self.offer_facts,
            "target_audiences" : [t.to_dict() for t in self.target_audiences],
            "offer_source_elements": [e.to_dict() for e in self._sorted_offer_source_elements()],
        }

        return {k: v for k, v in data.items() if k not in exclude}

    def to_content_dict(self):
        data = self.to_dict(exclude=["id", "offer_id"])
        data["target_audiences"] = [t.to_content_dict() for t in self.target_audiences]
        data["offer_source_elements"] = [e.to_content_dict() for e in self._sorted_offer_source_elements()]
        data["offer_facts"] = [{key: value for key, value in fact.items() if key not in {"id", "offer_source_id", "created_at", "updated_at", "is_reviewed", "evidence"}} for fact in self.offer_facts]
        return data

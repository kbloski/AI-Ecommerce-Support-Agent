from typing import Optional
from common.mixins.json_serializable import JSONSerializable

class OfferSourceDto(JSONSerializable):


    def __init__(
        self,
        id: int,
        offer_id: int,
        offer_details: Optional[str] = None,
    ):
        self.offer_facts = []
        self.id = id
        self.offer_id = offer_id
        self.offer_details = offer_details

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "offer_id": self.offer_id,
            "offer_details": self.offer_details,
            "offer_facts": self.offer_facts,
        }

        return {k: v for k, v in data.items() if k not in exclude}

    def to_content_dict(self):
        data = self.to_dict(exclude=["id", "offer_id"])
        data["offer_facts"] = [{key: value for key, value in fact.items() if key not in {"id", "offer_source_id", "created_at", "updated_at", "is_reviewed", "evidence"}} for fact in self.offer_facts]
        return data

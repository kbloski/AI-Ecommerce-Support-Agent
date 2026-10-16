from typing import Optional, List
from common.mixins.json_serializable import JSONSerializable
from .checklist_item_dto import ChecklistItemDto

class ChecklistDto(JSONSerializable):
    checklist_items : List[ChecklistItemDto] = []

    def __init__(
        self,
        id: int,
        offer_profile_id: int,
        name: str,
    ):
        self.id = id
        self.offer_profile_id = offer_profile_id
        self.name = name

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "offer_profile_id": self.offer_profile_id,
            "name" : self.name,
            "checklist_items" : self.checklist_items
        }

        return {k: v for k, v in data.items() if k not in exclude}

    def to_content_dict(self):
        return {
            "name": self.name,
            "checklist_items": [
                item.to_content_dict()
                for item in self.checklist_items
            ],
        }

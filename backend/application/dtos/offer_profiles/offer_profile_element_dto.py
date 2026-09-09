from datetime import datetime
from typing import Optional

from common.mixins.json_serializable import JSONSerializable


class OfferProfileElementDto(JSONSerializable):
    def __init__(
        self,
        id: int,
        offer_profile_id: int,
        type: str,
        name: str,
        description: Optional[str],
        is_reviewed: bool,
        created_at: Optional[datetime],
        updated_at: Optional[datetime],
    ):
        self.id = id
        self.offer_profile_id = offer_profile_id
        self.type = type
        self.name = name
        self.description = description
        self.is_reviewed = is_reviewed
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])
        data = {
            "id": self.id,
            "offer_profile_id": self.offer_profile_id,
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "is_reviewed": self.is_reviewed,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return {key: value for key, value in data.items() if key not in exclude}

    def to_content_dict(self):
        return self.to_dict(exclude=["id", "offer_profile_id", "created_at", "updated_at", "is_reviewed"])

from typing import Any, Dict, List, Optional

from common.mixins.json_serializable import JSONSerializable


class CreativeAngleDto(JSONSerializable):
    def __init__(
        self,
        id: str,
        name: str,
        description: Optional[str],
        purpose: Optional[str],
        rules: List[str],
    ):
        self.id = id
        self.name = name
        self.description = description
        self.purpose = purpose
        self.rules = rules

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreativeAngleDto":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            purpose=data.get("purpose"),
            rules=data.get("rules", []),
        )

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "purpose": self.purpose,
            "rules": self.rules,
        }
        return {key: value for key, value in data.items() if key not in exclude}

    def to_content_dict(self):
        return self.to_dict(exclude={"id"})

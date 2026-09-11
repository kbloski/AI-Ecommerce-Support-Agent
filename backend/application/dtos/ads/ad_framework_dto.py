from typing import Any, Dict, List, Optional

from common.mixins.json_serializable import JSONSerializable


class AdFrameworkDto(JSONSerializable):
    def __init__(
        self,
        id: str,
        name: str,
        format: Optional[str],
        goal: Optional[str],
        description: Optional[str],
        rules: List[str],
        structure: List[Dict[str, Any]],
    ):
        self.id = id
        self.name = name
        self.format = format
        self.goal = goal
        self.description = description
        self.rules = rules
        self.structure = structure

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdFrameworkDto":
        return cls(
            id=data["id"],
            name=data["name"],
            format=data.get("format"),
            goal=data.get("goal"),
            description=data.get("description"),
            rules=data.get("rules", []),
            structure=data.get("structure", []),
        )

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])
        data = {
            "id": self.id,
            "name": self.name,
            "format": self.format,
            "goal": self.goal,
            "description": self.description,
            "rules": self.rules,
            "structure": self.structure,
        }
        return {key: value for key, value in data.items() if key not in exclude}

    def to_content_dict(self):
        return self.to_dict(exclude={"id"})

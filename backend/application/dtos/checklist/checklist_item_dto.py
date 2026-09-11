from typing import Optional

from common.mixins.json_serializable import JSONSerializable


class ChecklistItemDto(JSONSerializable):
    def __init__(
        self,
        id: int,
        checklist_id: int,
        title: str,
        description: Optional[str],
        note: Optional[str],
        is_reviewed: bool,
    ):
        self.id = id
        self.checklist_id = checklist_id
        self.title = title
        self.description = description
        self.note = note
        self.is_reviewed = is_reviewed

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "checklist_id": self.checklist_id,
            "title": self.title,
            "description": self.description,
            "note": self.note,
            "is_reviewed": self.is_reviewed,
        }

        return {k: v for k, v in data.items() if k not in exclude}

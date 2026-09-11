from typing import List

from common.mixins.json_serializable import JSONSerializable
from .page_section_requirement_dto import PageSectionRequirementDto


class PageRequirementsDto(JSONSerializable):
    def __init__(
        self,
        id: int,
        page_strategy_id: int,
        name: str,
    ):
        self.id = id
        self.page_strategy_id = page_strategy_id
        self.name = name
        self.page_section_requirements: List[PageSectionRequirementDto] = []

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "page_strategy_id": self.page_strategy_id,
            "name": self.name,
            "page_section_requirements": [
                item.to_dict() for item in self.page_section_requirements
            ],
        }

        return {k: v for k, v in data.items() if k not in exclude}

    def to_content_dict(self):
        return {
            "name": self.name,
            "page_section_requirements": [
                item.to_content_dict() for item in self.page_section_requirements
            ],
        }

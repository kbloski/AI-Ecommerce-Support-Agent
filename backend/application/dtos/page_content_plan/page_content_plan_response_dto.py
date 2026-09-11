from typing import Optional, List

from common.mixins.json_serializable import JSONSerializable


class PageContentPlanDto(JSONSerializable):

    def __init__(
        self,
        id: int,
        name: str,
        page_blueprint_id: Optional[int],
        sections: Optional[List[dict]],
    ):
        self.id = id
        self.name = name
        self.page_blueprint_id = page_blueprint_id
        self.sections = sections

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "name": self.name,
            "page_blueprint_id": self.page_blueprint_id,
            "sections": self.sections,
        }

        return {k: v for k, v in data.items() if k not in exclude}

    def to_content_dict(self):
        return {
            "name": self.name,
            "sections": self.sections,
        }

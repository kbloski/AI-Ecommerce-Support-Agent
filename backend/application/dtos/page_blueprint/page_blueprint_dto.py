from common.mixins.json_serializable import JSONSerializable


class PageBlueprintDto(JSONSerializable):
    def __init__(self, id, offer_profile_id, name, description=""):
        self.id = id
        self.offer_profile_id = offer_profile_id
        self.name = name
        self.description = description or ""
        self.sections = []

    def to_dict(self, exclude=None):
        data = {"id": self.id, "offer_profile_id": self.offer_profile_id,
                "name": self.name, "description": self.description, "sections": self.sections}
        return {key: value for key, value in data.items() if key not in (exclude or [])}

    def to_content_dict(self):
        return {"name": self.name, "description": self.description,
                "sections": [{key: value for key, value in section.items() if key != "id"} for section in self.sections]}

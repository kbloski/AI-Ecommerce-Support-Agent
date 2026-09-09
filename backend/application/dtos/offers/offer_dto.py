from common.mixins.json_serializable import JSONSerializable


class OfferDto(JSONSerializable):
    def __init__(
        self,
        id: int,
        name: str,
        description: str | None,
    ):
        self.id = id
        self.name = name
        self.description = description

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

        return {k: v for k, v in data.items() if k not in exclude}

    def to_content_dict(self):
        data = self.to_dict(exclude=["id"])
        return data

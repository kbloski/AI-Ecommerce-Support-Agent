from common.mixins.json_serializable import JSONSerializable


class GenerateAdDto(JSONSerializable):

    def __init__(
        self,
        id: int,
        creative_execution_setup_id: int,
        name: str,
        content_json: dict,
    ):
        self.id = id
        self.creative_execution_setup_id = creative_execution_setup_id
        self.name = name
        self.content_json = content_json

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "creative_execution_setup_id": self.creative_execution_setup_id,
            "name": self.name,
            "content_json": self.content_json,
        }

        return {k: v for k, v in data.items() if k not in exclude}

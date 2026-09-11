from typing import Optional

from common.mixins.json_serializable import JSONSerializable


class AdSetupDto(JSONSerializable):

    def __init__(
        self,
        id: int,
        creative_strategy_id: int,
        name: Optional[str],
        creative_type: str,
        platform: Optional[str],
        format: Optional[str],
    ):
        self.id = id
        self.creative_strategy_id = creative_strategy_id
        self.name = name
        self.creative_type = creative_type
        self.platform = platform
        self.format = format

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "creative_strategy_id": self.creative_strategy_id,
            "name": self.name,
            "creative_type": self.creative_type,
            "platform": self.platform,
            "format": self.format,
        }

        return {k: v for k, v in data.items() if k not in exclude}

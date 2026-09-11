import json
from typing import List, Optional

from application.dtos.ads.creative_angle_dto import CreativeAngleDto

from infrastructure.logging.logger import Logger
from infrastructure.services.path_service import PathService


class CreativeAnglesRepository:
    def __init__(self, logger: Logger, path_service: PathService):
        self.logger = logger
        self.path_service = path_service

    def get_all(self) -> List[CreativeAngleDto]:
        with open(self.path_service.CREATIVE_ANGELS_FILE, "r", encoding="utf-8") as file:
            return [CreativeAngleDto.from_dict(item) for item in json.load(file)]

    def get_by_id(self, creative_angle_id: str) -> Optional[CreativeAngleDto]:
        for angle in self.get_all():
            if angle.id == creative_angle_id:
                return angle
        return None

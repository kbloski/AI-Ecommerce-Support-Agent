import json
from typing import List, Optional

from application.dtos.ads.ad_framework_dto import AdFrameworkDto

from infrastructure.logging.logger import Logger
from infrastructure.services.path_service import PathService


class AdFrameworksRepository:
    def __init__(self, logger: Logger, path_service: PathService):
        self.logger = logger
        self.path_service = path_service

    def get_all(self) -> List[AdFrameworkDto]:
        with open(self.path_service.AD_FRAMEWORKS_FILE, "r", encoding="utf-8") as file:
            return [AdFrameworkDto.from_dict(item) for item in json.load(file)]

    def get_by_id(self, framework_id: str) -> Optional[AdFrameworkDto]:
        for framework in self.get_all():
            if framework.id == framework_id:
                return framework
        return None

import json
from typing import List, Optional

from application.dtos.ads.execution_style_dto import ExecutionStyleDto

from infrastructure.logging.logger import Logger
from infrastructure.services.path_service import PathService


class ExecutionStylesRepository:
    def __init__(self, logger: Logger, path_service: PathService):
        self.logger = logger
        self.path_service = path_service

    def get_all(self) -> List[ExecutionStyleDto]:
        with open(self.path_service.EXECUTION_STYLES_FILE, "r", encoding="utf-8") as file:
            return [ExecutionStyleDto.from_dict(item) for item in json.load(file)]

    def get_by_id(self, execution_style_id: str) -> Optional[ExecutionStyleDto]:
        for execution_style in self.get_all():
            if execution_style.id == execution_style_id:
                return execution_style
        return None

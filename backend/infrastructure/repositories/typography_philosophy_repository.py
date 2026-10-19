import json

from infrastructure.logging.logger import Logger
from infrastructure.services.path_service import PathService


class TypographyPhilosophyRepository:
    def __init__(self, logger: Logger, path_service: PathService):
        self.logger = logger
        self.path_service = path_service

    def get(self) -> dict:
        with open(self.path_service.TYPOGRAPHY_PHILOSOPHY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

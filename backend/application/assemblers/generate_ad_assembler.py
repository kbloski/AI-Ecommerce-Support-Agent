from infrastructure.logging.logger import Logger
from application.dtos.generate_ad.generate_ad_response_dto import GenerateAdDto


class GenerateAdAssembler:
    def __init__(self, logger: Logger):
        self.logger = logger

    def assemble_dto(self, item: GenerateAdDto) -> GenerateAdDto:
        return item

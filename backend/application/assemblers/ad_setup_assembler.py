from infrastructure.logging.logger import Logger
from application.dtos.ad_setup.ad_setup_response_dto import AdSetupDto


class AdSetupAssembler:
    def __init__(self, logger: Logger):
        self.logger = logger

    def assemble_dto(self, item: AdSetupDto) -> AdSetupDto:
        return item

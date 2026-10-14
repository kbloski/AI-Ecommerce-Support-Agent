from application.dtos.audience.target_audience_dto import TargetAudienceDto
from infrastructure.logging.logger import Logger
from infrastructure.repositories.offer_source_repository import OfferSourceRepository

class TargetAudienceAssembler:
    def __init__(
        self,
        logger : Logger
    ):
        self.logger=logger

    def assemble_dto(self, item : TargetAudienceDto) -> TargetAudienceDto:
        return item



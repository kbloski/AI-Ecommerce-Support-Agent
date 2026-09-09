from infrastructure.repositories.offers_repository import OffersRepository
from application.dtos.offers.offer_dto import OfferDto
from infrastructure.logging.logger import Logger

class OfferAssembler:
    def __init__(
        self,
        logger : Logger,
        offers_repository: OffersRepository,
    ):
        self.offers_repository = offers_repository

    def assemble_dto(self, item : OfferDto) -> OfferDto:
        return item



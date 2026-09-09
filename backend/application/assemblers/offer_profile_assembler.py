from application.dtos.offer_profiles.offer_profile_dto import OfferProfileDto
from application.mappers.target_audience_mapper import TargetAudienceMapper
from infrastructure.logging.logger import Logger
from infrastructure.repositories.offer_profile_repository import OfferProfileRepository
from infrastructure.repositories.target_audiences_repository import TargetAudiencesRepository

class OfferProfileAssembler:
    def __init__(
        self,
        logger : Logger,
        offer_profile_repository : OfferProfileRepository,
        target_audiences_repository : TargetAudiencesRepository
    ):
        self.offer_profile_repository = offer_profile_repository
        self.target_audiences_repository = target_audiences_repository

    def assemble_dto(self, item : OfferProfileDto) -> OfferProfileDto:
        # item
        target_audiences = self.target_audiences_repository.find_for_offer_profile(offer_profile_id=item.id)
        item.target_audiences = [
            TargetAudienceMapper.to_dto(t)
            for t in target_audiences
        ]

        return item

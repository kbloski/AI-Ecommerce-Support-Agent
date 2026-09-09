from application.dtos.offer_profiles.offer_profile_dto import OfferProfileDto
from application.mappers.offer_profile_element_mapper import OfferProfileElementMapper
from application.mappers.target_audience_mapper import TargetAudienceMapper
from infrastructure.logging.logger import Logger
from infrastructure.repositories.offer_profile_repository import OfferProfileRepository
from infrastructure.repositories.target_audiences_repository import TargetAudiencesRepository
from infrastructure.repositories.offer_profile_elements_repository import OfferProfileElementsRepository

class OfferProfileAssembler:
    def __init__(
        self,
        logger : Logger,
        offer_profile_repository : OfferProfileRepository,
        target_audiences_repository : TargetAudiencesRepository,
        offer_profile_elements_repository : OfferProfileElementsRepository
    ):
        self.offer_profile_repository = offer_profile_repository
        self.target_audiences_repository = target_audiences_repository
        self.offer_profile_elements_repository = offer_profile_elements_repository

    def assemble_dto(self, item : OfferProfileDto) -> OfferProfileDto:
        # item
        target_audiences = self.target_audiences_repository.find_for_offer_profile(offer_profile_id=item.id)
        item.target_audiences = [
            TargetAudienceMapper.to_dto(t)
            for t in target_audiences
        ]

        offer_profile_elements = self.offer_profile_elements_repository.find_for_offer_profile(
            offer_profile_id=item.id
        )
        item.offer_profile_elements = [
            OfferProfileElementMapper.to_dto(element)
            for element in offer_profile_elements
        ]

        return item

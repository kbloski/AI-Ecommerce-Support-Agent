from typing import List

from infrastructure.logging.logger import Logger
from domain.models.creative.ugc_creative import UgcCreative
from application.dtos.ugc_creatives.ugc_creative_response_dto import UgcCreativeDto
from infrastructure.repositories.ugc_creative_repository import UgcCreativeRepository
from application.mappers.ugc_creative_mapper import UgcCreativeMapper
from application.assemblers.ugc_creative_assembler import UgcCreativeAssembler


class UgcCreativeService:

    def __init__(
        self,
        logger: Logger,
        ugc_creative_repository: UgcCreativeRepository,
        ugc_creative_assembler: UgcCreativeAssembler,
    ):
        self.logger = logger
        self.ugc_creative_repository = ugc_creative_repository
        self.ugc_creative_assembler = ugc_creative_assembler

    def create_ugc_creative(self, ugc_creative: UgcCreative) -> UgcCreativeDto:
        created = self.ugc_creative_repository.create(ugc_creative)
        return self.get_ugc_creative_by_id(id=created.id)

    def get_ugc_creative_by_id(self, id: int) -> UgcCreativeDto:
        ugc_creative_db = self.ugc_creative_repository.get_by_id(id)

        if not ugc_creative_db:
            raise ValueError(f"UGC creative {id} not found")

        ugc_creative_dto = UgcCreativeMapper.to_dto(ugc_creative_db)
        return self.ugc_creative_assembler.assemble_dto(ugc_creative_dto)

    def get_ugc_creatives_by_offer_profile(self, offer_profile_id: int) -> List[UgcCreativeDto]:
        items = self.ugc_creative_repository.get_by_offer_profile_id(offer_profile_id)
        dtos = [UgcCreativeMapper.to_dto(item) for item in items]
        return [self.ugc_creative_assembler.assemble_dto(dto) for dto in dtos]

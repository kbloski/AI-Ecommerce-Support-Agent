from typing import List

from infrastructure.logging.logger import Logger
from domain.models.generate_ad.generate_ad import GenerateAd
from application.dtos.generate_ad.generate_ad_response_dto import GenerateAdDto
from infrastructure.repositories.generate_ad_repository import GenerateAdRepository
from application.mappers.generate_ad_mapper import GenerateAdMapper
from application.assemblers.generate_ad_assembler import GenerateAdAssembler


class GenerateAdService:

    def __init__(
        self,
        logger: Logger,
        generate_ad_repository: GenerateAdRepository,
        generate_ad_assembler: GenerateAdAssembler,
    ):
        self.logger = logger
        self.generate_ad_repository = generate_ad_repository
        self.generate_ad_assembler = generate_ad_assembler

    def create_generate_ad(self, generate_ad: GenerateAd) -> GenerateAdDto:
        created = self.generate_ad_repository.create(generate_ad)
        return self.get_generate_ad_by_id(id=created.id)

    def get_generate_ad_by_id(self, id: int) -> GenerateAdDto:
        generate_ad_db = self.generate_ad_repository.get_by_id(id)

        if not generate_ad_db:
            raise ValueError(f"Generate Ad {id} not found")

        generate_ad_dto = GenerateAdMapper.to_dto(generate_ad_db)
        return self.generate_ad_assembler.assemble_dto(generate_ad_dto)

    def get_all_generate_ads(self) -> List[GenerateAdDto]:
        items = self.generate_ad_repository.get_all()
        dtos = [GenerateAdMapper.to_dto(item) for item in items]
        return [self.generate_ad_assembler.assemble_dto(dto) for dto in dtos]

    def get_generate_ads_by_setup(self, creative_execution_setup_id: int) -> List[GenerateAdDto]:
        items = self.generate_ad_repository.get_by_creative_execution_setup_id(creative_execution_setup_id)
        dtos = [GenerateAdMapper.to_dto(item) for item in items]
        return [self.generate_ad_assembler.assemble_dto(dto) for dto in dtos]

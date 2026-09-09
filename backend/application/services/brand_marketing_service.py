import json

from typing import List

from infrastructure.logging.logger import Logger
from domain.models.brand_marketing.brand_marketing import BrandMarketing
from application.dtos.brand_marketing.brand_marketing_response_dto import BrandMarketingDto
from infrastructure.repositories.brand_marketing_repository import BrandMarketingRepository
from application.mappers.brand_marketing_mapper import BrandMarketingMapper
from application.assemblers.brand_marketing_assembler import BrandMarketingAssembler
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class BrandMarketingService:

    def __init__(
        self,
        logger: Logger,
        brand_marketing_repository: BrandMarketingRepository,
        brand_marketing_assembler: BrandMarketingAssembler,
    ):
        self.logger = logger
        self.brand_marketing_repository = brand_marketing_repository
        self.brand_marketing_assembler = brand_marketing_assembler

    def create_brand_marketing(self, brand_marketing: BrandMarketing) -> BrandMarketingDto:
        created = self.brand_marketing_repository.create(brand_marketing)
        return self.get_brand_marketing_by_id(id=created.id)

    def get_brand_marketing_by_id(self, id: int) -> BrandMarketingDto:
        brand_marketing_db = self.brand_marketing_repository.get_by_id(id)

        if not brand_marketing_db:
            raise ValueError(f"Brand marketing {id} not found")

        brand_marketing_dto = BrandMarketingMapper.to_dto(brand_marketing_db)
        return self.brand_marketing_assembler.assemble_dto(brand_marketing_dto)

    def get_brand_marketings_by_offer_profile(self, offer_profile_id: int) -> List[BrandMarketingDto]:
        items = self.brand_marketing_repository.get_by_offer_profile_id(offer_profile_id)
        dtos = [BrandMarketingMapper.to_dto(item) for item in items]
        return [self.brand_marketing_assembler.assemble_dto(dto) for dto in dtos]

    def build_llm_context(self, brand_marketing_id: int) -> str:
        brand_marketing_json = json.dumps(
            self.get_brand_marketing_by_id(id=brand_marketing_id).to_content_dict(),
            ensure_ascii=False,
            indent=2,
            default=str
        )

        return build_llm_section("brand-marketing", brand_marketing_json, purpose=ContextSectionPurpose.BRAND_MARKETING.value)

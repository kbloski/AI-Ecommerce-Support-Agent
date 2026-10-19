import json

from application.mappers.page_blueprint_mapper import PageBlueprintMapper
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class PageBlueprintService:
    def __init__(self, logger, page_blueprint_repository, page_blueprint_assembler):
        self.logger = logger
        self.page_blueprint_repository = page_blueprint_repository
        self.page_blueprint_assembler = page_blueprint_assembler

    def create_page_blueprint(self, page_blueprint):
        created = self.page_blueprint_repository.create(page_blueprint)
        return self.get_page_blueprint_by_id(created.id)

    def get_page_blueprint_by_id(self, id):
        return self.get_page_blueprint_details_by_id(id)

    def get_page_blueprint_details_by_id(self, page_blueprint_id):
        item = self.page_blueprint_repository.get_by_id(page_blueprint_id)
        if item is None:
            raise LookupError(f"Page blueprint {page_blueprint_id} not found")
        return self.page_blueprint_assembler.assemble_dto(PageBlueprintMapper.to_dto(item))

    def get_page_blueprint_by_offer_profile(self, offer_profile_id):
        return [self.page_blueprint_assembler.assemble_dto(PageBlueprintMapper.to_dto(item))
                for item in self.page_blueprint_repository.get_by_offer_profile_id(offer_profile_id)]

    def build_llm_context(self, page_blueprint_id):
        content = self.get_page_blueprint_by_id(page_blueprint_id).to_content_dict()
        return build_llm_section("page-blueprints", json.dumps(content, ensure_ascii=False, indent=2),
                                 purpose=ContextSectionPurpose.PAGE_BLUEPRINT.value)

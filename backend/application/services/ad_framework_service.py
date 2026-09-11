import json

from infrastructure.logging.logger import Logger
from infrastructure.repositories.ad_frameworks_repository import AdFrameworksRepository
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class AdFrameworkService:

    def __init__(self, logger: Logger, ad_frameworks_repository: AdFrameworksRepository):
        self.logger = logger
        self.ad_frameworks_repository = ad_frameworks_repository

    def build_llm_context(self, ad_framework_id: str) -> str | None:
        ad_framework = self.ad_frameworks_repository.get_by_id(ad_framework_id)

        if ad_framework is None:
            return None

        ad_framework_json = json.dumps(
            ad_framework.to_content_dict(),
            ensure_ascii=False,
            indent=2,
        )

        return build_llm_section("ad-framework", ad_framework_json, purpose=ContextSectionPurpose.AD_FRAMEWORK.value)

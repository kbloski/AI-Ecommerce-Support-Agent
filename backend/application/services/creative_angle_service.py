import json

from infrastructure.logging.logger import Logger
from infrastructure.repositories.creative_angels_repository import CreativeAnglesRepository
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class CreativeAngleService:

    def __init__(self, logger: Logger, creative_angels_repository: CreativeAnglesRepository):
        self.logger = logger
        self.creative_angels_repository = creative_angels_repository

    def build_llm_context(self, creative_angle_id: str) -> str | None:
        creative_angle = self.creative_angels_repository.get_by_id(creative_angle_id)

        if creative_angle is None:
            return None

        creative_angle_json = json.dumps(
            creative_angle.to_content_dict(),
            ensure_ascii=False,
            indent=2,
        )

        return build_llm_section("creative-angle", creative_angle_json, purpose=ContextSectionPurpose.CREATIVE_ANGLE.value)

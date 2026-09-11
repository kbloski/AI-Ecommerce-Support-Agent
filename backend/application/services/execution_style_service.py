import json

from infrastructure.logging.logger import Logger
from infrastructure.repositories.execution_styles_repository import ExecutionStylesRepository
from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose


class ExecutionStyleService:

    def __init__(self, logger: Logger, execution_styles_repository: ExecutionStylesRepository):
        self.logger = logger
        self.execution_styles_repository = execution_styles_repository

    def build_llm_context(self, execution_style_id: str) -> str | None:
        execution_style = self.execution_styles_repository.get_by_id(execution_style_id)

        if execution_style is None:
            return None

        execution_style_json = json.dumps(
            execution_style.to_content_dict(),
            ensure_ascii=False,
            indent=2,
        )

        return build_llm_section("execution-style", execution_style_json, purpose=ContextSectionPurpose.EXECUTION_STYLE.value)

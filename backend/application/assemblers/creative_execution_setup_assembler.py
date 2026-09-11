from application.dtos.creative_execution_setup.creative_execution_setup_response_dto import CreativeExecutionSetupDto
from infrastructure.logging.logger import Logger
from infrastructure.repositories.ad_frameworks_repository import AdFrameworksRepository
from infrastructure.repositories.creative_angels_repository import CreativeAnglesRepository
from infrastructure.repositories.execution_styles_repository import ExecutionStylesRepository


class CreativeExecutionSetupAssembler:
    def __init__(
        self,
        logger: Logger,
        ad_frameworks_repository: AdFrameworksRepository,
        creative_angels_repository: CreativeAnglesRepository,
        execution_styles_repository: ExecutionStylesRepository,
    ):
        self.logger = logger
        self.ad_frameworks_repository = ad_frameworks_repository
        self.creative_angels_repository = creative_angels_repository
        self.execution_styles_repository = execution_styles_repository

    def assemble_dto(self, item: CreativeExecutionSetupDto) -> CreativeExecutionSetupDto:
        item.ad_framework = (
            self.ad_frameworks_repository.get_by_id(item.ad_framework_id)
            if item.ad_framework_id
            else None
        )
        item.creative_angle = (
            self.creative_angels_repository.get_by_id(item.creative_angle_id)
            if item.creative_angle_id
            else None
        )
        item.execution_style = (
            self.execution_styles_repository.get_by_id(item.execution_style_id)
            if item.execution_style_id
            else None
        )
        return item

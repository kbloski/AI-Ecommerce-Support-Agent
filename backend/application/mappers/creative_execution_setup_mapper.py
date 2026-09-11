from application.dtos.creative_execution_setup.creative_execution_setup_response_dto import CreativeExecutionSetupDto
from domain.models.creative_execution_setup.creative_execution_setup import CreativeExecutionSetup


class CreativeExecutionSetupMapper:
    @staticmethod
    def to_dto(item: CreativeExecutionSetup) -> CreativeExecutionSetupDto:
        return CreativeExecutionSetupDto(
            id=item.id,
            ad_setup_id=item.ad_setup_id,
            name=item.name,
            duration_seconds=item.duration_seconds,
            number_of_slides=item.number_of_slides,
            ad_framework_id=item.ad_framework_id,
            creative_angle_id=item.creative_angle_id,
            execution_style_id=item.execution_style_id,
            additional_instructions=item.additional_instructions,
        )

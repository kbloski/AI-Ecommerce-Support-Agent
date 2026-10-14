from domain.models.page.page_blueprint import PageBlueprint
from application.dtos.page_blueprint.page_blueprint_response_dto import PageBlueprintDto


class PageBlueprintMapper:

    @staticmethod
    def to_dto(item: PageBlueprint) -> PageBlueprintDto:
        return PageBlueprintDto(
            id=item.id,
            page_strategy_id=item.page_strategy_id,
            page_requirements_id=item.page_requirements_id,
            page_type=item.page_type,
            primary_conversion_goal=item.primary_conversion_goal,
            sections=item.sections,
        )

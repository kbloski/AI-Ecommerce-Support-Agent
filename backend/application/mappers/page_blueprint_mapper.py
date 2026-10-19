from domain.models.page.page_blueprint import PageBlueprint
from application.dtos.page_blueprint.page_blueprint_dto import PageBlueprintDto


class PageBlueprintMapper:

    @staticmethod
    def to_dto(item: PageBlueprint) -> PageBlueprintDto:
        return PageBlueprintDto(
            id=item.id,
            offer_profile_id=item.offer_profile_id,
            name=item.name,
            description=item.description,
        )

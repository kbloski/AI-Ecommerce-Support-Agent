from domain.models.page_requirements.page_requirements import PageRequirements
from application.dtos.page_requirements.page_requirements_dto import PageRequirementsDto


class PageRequirementsMapper:

    @staticmethod
    def to_dto(item: PageRequirements) -> PageRequirementsDto:
        return PageRequirementsDto(
            id=item.id,
            page_strategy_id=item.page_strategy_id,
            name=item.name,
        )

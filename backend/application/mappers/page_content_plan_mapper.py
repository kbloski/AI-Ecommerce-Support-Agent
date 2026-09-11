from domain.models.page_content_plan.page_content_plan import PageContentPlan
from application.dtos.page_content_plan.page_content_plan_response_dto import PageContentPlanDto


class PageContentPlanMapper:

    @staticmethod
    def to_dto(item: PageContentPlan) -> PageContentPlanDto:
        return PageContentPlanDto(
            id=item.id,
            name=item.name,
            page_blueprint_id=item.page_blueprint_id,
            sections=item.sections,
        )

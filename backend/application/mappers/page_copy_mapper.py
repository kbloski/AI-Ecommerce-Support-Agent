from domain.models.page.page_copy import PageCopy
from application.dtos.page_copy.page_copy_response_dto import PageCopyDto


class PageCopyMapper:

    @staticmethod
    def to_dto(item: PageCopy) -> PageCopyDto:
        return PageCopyDto(
            id=item.id,
            page_content_plan_id=item.page_content_plan_id,
            sections=item.sections,
        )

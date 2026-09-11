from domain.models.checklist.checklist_item import ChecklistItem
from application.dtos.checklist.checklist_item_dto import ChecklistItemDto

class ChecklistItemMapper:

    @staticmethod
    def to_dto(item : ChecklistItem) -> ChecklistItemDto:
        return ChecklistItemDto(
            id = item.id,
            checklist_id= item.checklist_id,
            title=item.title,
            description=item.description,
            note=item.note,
            is_reviewed=item.is_reviewed,
        )


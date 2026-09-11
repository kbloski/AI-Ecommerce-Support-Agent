from domain.models.checklist.checklist import Checklist
from application.dtos.checklist.checklist_dto import ChecklistDto

class ChecklistMapper:

    @staticmethod
    def to_dto(item : Checklist) -> ChecklistDto:
        return ChecklistDto(
            id = item.id,
            offer_profile_id=item.offer_profile_id,
            name=item.name,
        )


from infrastructure.logging.logger import Logger
from application.dtos.checklist.checklist_dto import ChecklistDto
from application.dtos.checklist.checklist_item_dto import ChecklistItemDto
from application.mappers.checklist_item_mapper import ChecklistItemMapper
from infrastructure.repositories.checklist_items_repository import ChecklistItemsRepository


class ChecklistAssembler:
    logger : Logger
    checklist_items_repository : ChecklistItemsRepository

    def __init__(
        self,
        logger : Logger,
        checklist_items_repository : ChecklistItemsRepository
    ):
        self.logger = logger
        self.checklist_items_repository = checklist_items_repository

    def assemble_dto(self, item : ChecklistDto) -> ChecklistDto:
        items_db = self.checklist_items_repository.find_for_checklist(checklist_id=item.id)
        checklist_items_dtos = [ChecklistItemMapper.to_dto(item=i) for i in items_db]
        item.checklist_items = checklist_items_dtos

        return item



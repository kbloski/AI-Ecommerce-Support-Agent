from di.container import Container
from application.mappers.checklist_item_mapper import ChecklistItemMapper


def update_checklist_item_handler(id: int, fields: dict):
    container = Container()
    repository = container.checklist_items_repository()
    item = repository.get_by_id(id)
    if item is None:
        raise LookupError(f"ChecklistItem with id {id} not found")

    if "is_reviewed" in fields:
        item.is_reviewed = fields["is_reviewed"]

    return ChecklistItemMapper.to_dto(repository.update(item)).to_dict()

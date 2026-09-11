from di.container import Container


def delete_checklist_handler(id: int):
    container = Container()
    checklist_repository = container.checklist_repository()
    checklist_items_repository = container.checklist_items_repository()

    checklist_items = checklist_items_repository.find_for_checklist(checklist_id=id)
    for checklist_item in checklist_items:
        checklist_items_repository.delete(id=checklist_item.id)

    deleted = checklist_repository.delete(id=id)

    return {"deleted": deleted}

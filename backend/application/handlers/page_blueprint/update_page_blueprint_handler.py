from fastapi import HTTPException

from application.dtos.page_blueprint.page_blueprint_fields import PageBlueprintFields
from di.container import Container
from infrastructure.database.unit_of_work import unit_of_work


def update_page_blueprint_handler(id: int, name: str, sections: list[dict], description: str = ""):
    fields = PageBlueprintFields(name=name, description=description, sections=sections)
    container = Container()
    repository = container.page_blueprint_repository()
    item = repository.get_by_id(id)
    if item is None:
        raise HTTPException(404, f"Page blueprint {id} not found")
    try:
        with unit_of_work(container.db()):
            container.page_blueprint_sections_repository().replace_for_blueprint(id, fields.sections)
            item.name = fields.name
            item.description = fields.description
            repository.update(item)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    return container.page_blueprint_service().get_page_blueprint_by_id(id)

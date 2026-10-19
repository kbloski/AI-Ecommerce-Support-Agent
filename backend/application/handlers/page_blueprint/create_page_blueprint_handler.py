from fastapi import HTTPException

from application.dtos.page_blueprint.page_blueprint_fields import PageBlueprintFields
from di.container import Container
from domain.models.page.page_blueprint import PageBlueprint
from domain.models.page.page_blueprint_section import PageBlueprintSection
from infrastructure.database.unit_of_work import unit_of_work


def create_page_blueprint_handler(offer_profile_id: int, name: str, sections: list[dict], description: str = ""):
    fields = PageBlueprintFields(name=name, description=description, sections=sections)
    if any(section.id is not None for section in fields.sections):
        raise HTTPException(422, "New sections must not specify existing IDs")
    container = Container()
    try:
        container.offer_profile_service().get_offer_profile_details_by_id(offer_profile_id)
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    with unit_of_work(container.db()):
        item = container.page_blueprint_repository().create(PageBlueprint(
            offer_profile_id=offer_profile_id, name=fields.name, description=fields.description,
        ))
        container.page_blueprint_sections_repository().create_many([
            PageBlueprintSection(page_blueprint_id=item.id, **section.model_dump(exclude={"id"}))
            for section in fields.sections
        ])
    return container.page_blueprint_service().get_page_blueprint_by_id(item.id)

from typing import Any, Dict, List

from di.container import Container
from domain.enums.page_section_requirement_type import PageSectionRequirementType
from domain.models.page_requirements.page_section_requirement import PageSectionRequirement
from infrastructure.database.unit_of_work import unit_of_work

ALLOWED_REQUIREMENT_TYPES = {item.value for item in PageSectionRequirementType}


def update_page_requirements_handler(id: int, section_requirements: List[Dict[str, Any]]):
    container = Container()

    page_requirements_repository = container.page_requirements_repository()
    page_section_requirements_repository = container.page_section_requirements_repository()
    page_sections_service = container.page_sections_service()
    page_requirements_service = container.page_requirements_service()

    if page_requirements_repository.get_by_id(id) is None:
        raise ValueError(f"Page requirements {id} not found")

    allowed_section_types = page_sections_service.get_allowed_ids()
    seen_section_types = set()

    for entry in section_requirements:
        section_type_id = entry.get("page_section_type_id")
        requirement_type = entry.get("requirement_type")

        if section_type_id not in allowed_section_types:
            raise ValueError(f"Invalid page_section_type_id: {section_type_id}")

        if requirement_type not in ALLOWED_REQUIREMENT_TYPES:
            raise ValueError(f"Invalid requirement_type: {requirement_type}")

        if section_type_id in seen_section_types:
            raise ValueError(f"Duplicate page_section_type_id: {section_type_id}")

        seen_section_types.add(section_type_id)

    items = [
        PageSectionRequirement(
            page_requirements_id=id,
            page_section_type_id=entry.get("page_section_type_id"),
            requirement_type=entry.get("requirement_type"),
            position=entry.get("position"),
        )
        for entry in section_requirements
    ]

    with unit_of_work(container.db()):
        page_section_requirements_repository.replace_for_page_requirements(
            page_requirements_id=id,
            items=items,
        )

    return page_requirements_service.get_page_requirements_by_id(id=id)

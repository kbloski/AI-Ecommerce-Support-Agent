from di.container import Container
from domain.enums.page_section_requirement_type import PageSectionRequirementType
from domain.models.page_requirements.page_requirements import PageRequirements
from domain.models.page_requirements.page_section_requirement import PageSectionRequirement
from infrastructure.database.unit_of_work import unit_of_work


ALLOWED_REQUIREMENT_TYPES = {item.value for item in PageSectionRequirementType}


def create_page_requirements_handler(
    page_strategy_id: int,
    name: str,
    section_requirements: list[dict],
):
    """Create user-authored Page Requirements without invoking the LLM."""
    container = Container()
    page_strategy_service = container.page_strategy_service()
    page_requirements_service = container.page_requirements_service()
    page_section_requirements_repository = container.page_section_requirements_repository()
    sections = container.page_sections_service().get_all()

    page_strategy_service.get_page_strategy_by_id(id=page_strategy_id)
    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("Page requirements name cannot be empty")

    allowed_ids = {section["id"] for section in sections}
    seen_ids = set()
    seen_positions = set()
    for item in section_requirements:
        section_id = item.get("page_section_type_id")
        requirement_type = item.get("requirement_type")
        position = item.get("position")
        if section_id not in allowed_ids:
            raise ValueError(f"Invalid page_section_type_id: {section_id}")
        if section_id in seen_ids:
            raise ValueError(f"Duplicate page_section_type_id: {section_id}")
        if requirement_type not in ALLOWED_REQUIREMENT_TYPES:
            raise ValueError(f"Invalid requirement_type for section: {section_id}")
        if position is not None and (not isinstance(position, int) or position < 1):
            raise ValueError(f"Invalid position for section: {section_id}")
        if position is not None and position in seen_positions:
            raise ValueError(f"Duplicate section position: {position}")
        seen_ids.add(section_id)
        if position is not None:
            seen_positions.add(position)

    created = page_requirements_service.create_page_requirements(PageRequirements(
        page_strategy_id=page_strategy_id,
        name=normalized_name,
    ))
    items = [
        PageSectionRequirement(
            page_requirements_id=created.id,
            page_section_type_id=item["page_section_type_id"],
            requirement_type=item["requirement_type"],
            position=item.get("position"),
        )
        for item in section_requirements
    ]
    with unit_of_work(container.db()):
        page_section_requirements_repository.create_many(items)

    return page_requirements_service.get_page_requirements_details_by_id(
        page_requirements_id=created.id
    )

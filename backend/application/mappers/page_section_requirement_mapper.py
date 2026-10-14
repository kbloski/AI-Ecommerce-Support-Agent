from domain.models.page.page_section_requirement import PageSectionRequirement
from application.dtos.page_requirements.page_section_requirement_dto import PageSectionRequirementDto


class PageSectionRequirementMapper:

    @staticmethod
    def to_dto(item: PageSectionRequirement) -> PageSectionRequirementDto:
        return PageSectionRequirementDto(
            id=item.id,
            page_requirements_id=item.page_requirements_id,
            page_section_type_id=item.page_section_type_id,
            requirement_type=item.requirement_type,
            position=item.position,
        )

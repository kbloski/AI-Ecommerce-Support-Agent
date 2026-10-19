class PageBlueprintAssembler:
    def __init__(self, logger, page_blueprint_sections_repository):
        self.logger = logger
        self.page_blueprint_sections_repository = page_blueprint_sections_repository

    def assemble_dto(self, item):
        item.sections = [
            {"id": section.id, "type": section.type, "name": section.name,
             "purpose": section.purpose, "position": section.position, "is_optional": section.is_optional}
            for section in self.page_blueprint_sections_repository.find_for_blueprint(item.id)
        ]
        return item

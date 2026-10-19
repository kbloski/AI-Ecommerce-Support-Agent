from domain.models.page.page_blueprint_section import PageBlueprintSection


class PageBlueprintSectionsRepository:
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db

    def find_for_blueprint(self, page_blueprint_id):
        return self.db.query(PageBlueprintSection).filter(
            PageBlueprintSection.page_blueprint_id == page_blueprint_id
        ).order_by(PageBlueprintSection.position, PageBlueprintSection.id).all()

    def create_many(self, items):
        self.db.add_all(items)
        self.db.flush()
        return items

    def replace_for_blueprint(self, page_blueprint_id, sections):
        existing = {item.id: item for item in self.find_for_blueprint(page_blueprint_id)}
        supplied_ids = [section.id for section in sections if section.id is not None]
        if len(supplied_ids) != len(set(supplied_ids)) or not set(supplied_ids).issubset(existing):
            raise ValueError("Section IDs must belong to this blueprint and may occur only once")
        for item_id, item in existing.items():
            if item_id not in supplied_ids:
                self.db.delete(item)
        for section in sections:
            values = section.model_dump(exclude={"id"})
            if section.id is None:
                self.db.add(PageBlueprintSection(page_blueprint_id=page_blueprint_id, **values))
            else:
                for key, value in values.items():
                    setattr(existing[section.id], key, value)
        self.db.flush()

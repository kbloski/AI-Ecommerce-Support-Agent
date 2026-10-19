class PageService:
    def __init__(self, page_repository):
        self.page_repository = page_repository

    def get_by_id(self, page_id: int) -> dict:
        page = self.page_repository.get_by_id(page_id)
        if page is None:
            raise LookupError(f"Page {page_id} not found")
        return self._to_dict(page)

    def get_by_offer_profile_id(self, offer_profile_id: int) -> list[dict]:
        return [self._to_dict(page) for page in self.page_repository.get_by_offer_profile_id(offer_profile_id)]

    def _to_dict(self, page) -> dict:
        return {
            "id": page.id,
            "offer_profile_id": page.offer_profile_id,
            "page_blueprint_id": page.page_blueprint_id,
            "name": page.name,
            "description": page.description,
            "is_favorite": page.is_favorite,
            "sections": [
                {"id": section.id, "type": section.type, "name": section.name,
                 "content": section.content, "position": section.position}
                for section in self.page_repository.get_sections(page.id)
            ],
        }

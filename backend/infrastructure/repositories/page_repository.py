from sqlalchemy.orm import Session

from domain.models.page.page import Page
from domain.models.page.page_section import PageSection


class PageRepository:
    def __init__(self, logger, db: Session):
        self.logger = logger
        self.db = db

    def create(self, page: Page, sections: list[PageSection]) -> Page:
        self.db.add(page)
        self.db.flush()
        for section in sections:
            section.page_id = page.id
            self.db.add(section)
        self.db.flush()
        return page

    def get_by_id(self, page_id: int) -> Page | None:
        return self.db.query(Page).filter(Page.id == page_id).first()

    def get_by_offer_profile_id(self, offer_profile_id: int) -> list[Page]:
        return self.db.query(Page).filter(Page.offer_profile_id == offer_profile_id).order_by(Page.id.desc()).all()

    def get_sections(self, page_id: int) -> list[PageSection]:
        return self.db.query(PageSection).filter(PageSection.page_id == page_id).order_by(PageSection.position, PageSection.id).all()

    def delete(self, page_id: int) -> bool:
        page = self.get_by_id(page_id)
        if page is None:
            return False
        self.db.delete(page)
        self.db.commit()
        return True

from typing import Literal

from sqlalchemy import func, or_
from sqlalchemy.orm import Query, Session

from common.results.paginated_result import PaginatedResult
from domain.enums.offer_profile_element_type import OfferProfileElementType
from domain.models.offer_profiles.offer_profile_element import OfferProfileElement
from infrastructure.logging.logger import Logger


class OfferProfileElementsRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    def find_for_offer_profile(self, offer_profile_id: int) -> list[OfferProfileElement]:
        return (
            self.db.query(OfferProfileElement)
            .filter(OfferProfileElement.offer_profile_id == offer_profile_id)
            .order_by(
                OfferProfileElement.type.asc(),
                OfferProfileElement.name.asc(),
                OfferProfileElement.id.asc(),
            )
            .all()
        )

    def search_for_offer_profile(
        self,
        offer_profile_id: int,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        element_type: OfferProfileElementType | None = None,
        is_reviewed: bool | None = None,
        sort: Literal["created_at_desc", "created_at_asc", "name_asc", "name_desc"] = "created_at_desc",
    ) -> PaginatedResult[OfferProfileElement]:
        page = max(1, page)
        page_size = max(1, page_size)

        query: Query = self.db.query(OfferProfileElement).filter(
            OfferProfileElement.offer_profile_id == offer_profile_id
        )

        if search and (normalized_search := search.strip()):
            search_pattern = f"%{normalized_search}%"
            query = query.filter(or_(
                OfferProfileElement.name.ilike(search_pattern),
                OfferProfileElement.description.ilike(search_pattern),
            ))

        if element_type is not None:
            query = query.filter(OfferProfileElement.type == element_type)

        if is_reviewed is not None:
            query = query.filter(OfferProfileElement.is_reviewed == is_reviewed)

        order_by = {
            "created_at_desc": (
                OfferProfileElement.is_reviewed.asc(),
                OfferProfileElement.created_at.desc(),
                OfferProfileElement.id.desc(),
            ),
            "created_at_asc": (OfferProfileElement.created_at.asc(), OfferProfileElement.id.asc()),
            "name_asc": (OfferProfileElement.name.asc(), OfferProfileElement.id.asc()),
            "name_desc": (OfferProfileElement.name.desc(), OfferProfileElement.id.desc()),
        }

        total_items = query.with_entities(func.count(OfferProfileElement.id)).scalar() or 0
        items = (
            query
            .order_by(*order_by[sort])
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return PaginatedResult(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
        )

    def create(self, element: OfferProfileElement) -> OfferProfileElement:
        self.db.add(element)
        self.db.commit()
        self.db.refresh(element)
        return element

    def get_by_id(self, id: int) -> OfferProfileElement | None:
        return self.db.query(OfferProfileElement).filter(OfferProfileElement.id == id).first()

    def update(self, element: OfferProfileElement) -> OfferProfileElement:
        existing_element = self.get_by_id(element.id)

        if not existing_element:
            raise ValueError(f"OfferProfileElement with id {element.id} not found")

        for key, value in element.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_element, key, value)

        self.db.commit()
        self.db.refresh(existing_element)

        return existing_element

    def delete(self, id: int) -> bool:
        element = self.get_by_id(id)

        if not element:
            return False

        self.db.delete(element)
        self.db.commit()
        return True

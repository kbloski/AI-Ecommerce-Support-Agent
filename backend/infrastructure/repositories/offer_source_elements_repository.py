from typing import Literal

from sqlalchemy import func, or_
from sqlalchemy.orm import Query, Session

from common.results.paginated_result import PaginatedResult
from domain.enums.offer_source_element_type import OfferSourceElementType
from domain.models.offer.offer_source_element import OfferSourceElement
from infrastructure.logging.logger import Logger


class OfferSourceElementsRepository:
    def __init__(self, logger: Logger, db: Session):
        self.logger = logger
        self.db = db

    def find_for_offer_source(self, offer_source_id: int) -> list[OfferSourceElement]:
        return (
            self.db.query(OfferSourceElement)
            .filter(OfferSourceElement.offer_source_id == offer_source_id)
            .order_by(
                OfferSourceElement.type.asc(),
                OfferSourceElement.name.asc(),
                OfferSourceElement.id.asc(),
            )
            .all()
        )

    def search_for_offer_source(
        self,
        offer_source_id: int,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        element_type: OfferSourceElementType | None = None,
        is_reviewed: bool | None = None,
        sort: Literal["created_at_desc", "created_at_asc", "name_asc", "name_desc"] = "created_at_desc",
    ) -> PaginatedResult[OfferSourceElement]:
        page = max(1, page)
        page_size = max(1, page_size)

        query: Query = self.db.query(OfferSourceElement).filter(
            OfferSourceElement.offer_source_id == offer_source_id
        )

        if search and (normalized_search := search.strip()):
            search_pattern = f"%{normalized_search}%"
            query = query.filter(or_(
                OfferSourceElement.name.ilike(search_pattern),
                OfferSourceElement.description.ilike(search_pattern),
            ))

        if element_type is not None:
            query = query.filter(OfferSourceElement.type == element_type)

        if is_reviewed is not None:
            query = query.filter(OfferSourceElement.is_reviewed == is_reviewed)

        order_by = {
            "created_at_desc": (
                OfferSourceElement.is_reviewed.asc(),
                OfferSourceElement.created_at.desc(),
                OfferSourceElement.id.desc(),
            ),
            "created_at_asc": (OfferSourceElement.created_at.asc(), OfferSourceElement.id.asc()),
            "name_asc": (OfferSourceElement.name.asc(), OfferSourceElement.id.asc()),
            "name_desc": (OfferSourceElement.name.desc(), OfferSourceElement.id.desc()),
        }

        total_items = query.with_entities(func.count(OfferSourceElement.id)).scalar() or 0
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

    def create(self, element: OfferSourceElement) -> OfferSourceElement:
        self.db.add(element)
        self.db.commit()
        self.db.refresh(element)
        return element

    def get_by_id(self, id: int) -> OfferSourceElement | None:
        return self.db.query(OfferSourceElement).filter(OfferSourceElement.id == id).first()

    def update(self, element: OfferSourceElement) -> OfferSourceElement:
        existing_element = self.get_by_id(element.id)

        if not existing_element:
            raise ValueError(f"OfferSourceElement with id {element.id} not found")

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

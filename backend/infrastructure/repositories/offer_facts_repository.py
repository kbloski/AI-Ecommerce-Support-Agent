from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from common.results.paginated_result import PaginatedResult
from domain.models.offer.offer_fact import OfferFact


class OfferFactsRepository:
    def __init__(self, logger, db: Session):
        self.db = db

    def find_for_offer_source(self, offer_source_id):
        return self.db.query(OfferFact).filter(OfferFact.offer_source_id == offer_source_id).order_by(OfferFact.id).all()

    def search_for_offer_source(self, offer_source_id, page=1, page_size=20, search=None, is_reviewed=None, sort="created_at_desc"):
        query = self.db.query(OfferFact).filter(OfferFact.offer_source_id == offer_source_id)
        if search and search.strip():
            pattern = f"%{search.strip()}%"
            query = query.filter(or_(OfferFact.name.ilike(pattern), OfferFact.description.ilike(pattern), OfferFact.evidence.ilike(pattern)))
        if is_reviewed is not None:
            query = query.filter(OfferFact.is_reviewed == is_reviewed)
        orders = {
            "created_at_desc": (OfferFact.is_reviewed.asc(), OfferFact.created_at.desc(), OfferFact.id.desc()),
            "created_at_asc": (OfferFact.created_at.asc(), OfferFact.id.asc()),
            "name_asc": (OfferFact.name.asc(), OfferFact.id.asc()),
            "name_desc": (OfferFact.name.desc(), OfferFact.id.desc()),
        }
        count = query.with_entities(func.count(OfferFact.id)).scalar() or 0
        items = query.order_by(*orders[sort]).offset((page - 1) * page_size).limit(page_size).all()
        return PaginatedResult(items=items, page=page, page_size=page_size, total_items=count)

    def get_by_id(self, id):
        return self.db.query(OfferFact).filter(OfferFact.id == id).first()

    def create_many(self, facts):
        try:
            self.db.add_all(facts)
            self.db.commit()
            for fact in facts:
                self.db.refresh(fact)
            return facts
        except Exception:
            self.db.rollback()
            raise

    def update(self, fact):
        self.db.commit()
        self.db.refresh(fact)
        return fact

    def delete(self, fact):
        self.db.delete(fact)
        self.db.commit()

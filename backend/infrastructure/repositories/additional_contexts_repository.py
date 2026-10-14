from domain.models.context.additional_context import AdditionalContext
from domain.models.offer.offer_profile_additional_context import OfferProfileAdditionalContext


class AdditionalContextsRepository:
    def __init__(self, logger, db):
        self.db = db

    def list_all(self):
        return self.db.query(AdditionalContext).order_by(AdditionalContext.name, AdditionalContext.id).all()

    def get_by_id(self, id):
        return self.db.get(AdditionalContext, id)

    def find_for_offer_profile(self, offer_profile_id):
        return self.db.query(AdditionalContext).join(OfferProfileAdditionalContext, OfferProfileAdditionalContext.additional_context_id == AdditionalContext.id).filter(OfferProfileAdditionalContext.offer_profile_id == offer_profile_id).order_by(AdditionalContext.name, AdditionalContext.id).all()

    def create_for_offer_profile(self, offer_profile_id, context):
        try:
            self.db.add(context)
            self.db.flush()
            self.db.add(OfferProfileAdditionalContext(offer_profile_id=offer_profile_id, additional_context_id=context.id))
            self.db.commit()
            self.db.refresh(context)
            return context
        except Exception:
            self.db.rollback()
            raise

    def update(self, context):
        self.db.commit()
        self.db.refresh(context)
        return context

    def attach(self, offer_profile_id, additional_context_id):
        if self.db.get(OfferProfileAdditionalContext, (offer_profile_id, additional_context_id)) is None:
            self.db.add(OfferProfileAdditionalContext(offer_profile_id=offer_profile_id, additional_context_id=additional_context_id))
            self.db.commit()

    def detach(self, offer_profile_id, additional_context_id):
        link = self.db.get(OfferProfileAdditionalContext, (offer_profile_id, additional_context_id))
        if link is not None:
            self.db.delete(link)
            self.db.commit()

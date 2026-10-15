from domain.models.offer.offer_profile import OfferProfile


class OfferProfilesRepository:
    def __init__(self, logger, db):
        self.db = db

    def find_all(self):
        return self.db.query(OfferProfile).order_by(OfferProfile.id.desc()).all()

    def find_for_offer_source(self, offer_source_id):
        return self.db.query(OfferProfile).filter(OfferProfile.offer_source_id == offer_source_id).order_by(OfferProfile.id.desc()).all()

    def create(self, profile):
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_by_id(self, id):
        return self.db.query(OfferProfile).filter(OfferProfile.id == id).first()

    def update(self, profile):
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, profile):
        self.db.delete(profile)
        self.db.commit()

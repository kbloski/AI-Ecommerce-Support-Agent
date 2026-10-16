from domain.models.ad.ad_copy import AdCopy


class AdCopiesRepository:
    def __init__(self, logger, db):
        self.db = db

    def find_for_offer_profile(self, offer_profile_id):
        return self.db.query(AdCopy).filter(AdCopy.offer_profile_id == offer_profile_id).order_by(AdCopy.id.desc()).all()

    def get_by_id(self, id):
        return self.db.get(AdCopy, id)

    def create_many(self, items):
        try:
            self.db.add_all(items)
            self.db.commit()
            for item in items:
                self.db.refresh(item)
            return items
        except Exception:
            self.db.rollback()
            raise

    def update(self, item):
        try:
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception:
            self.db.rollback()
            raise

    def delete(self, item):
        try:
            self.db.delete(item)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

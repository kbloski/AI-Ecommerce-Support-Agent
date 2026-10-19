from domain.models.brand.brand_style import BrandStyle


class BrandStylesRepository:
    def __init__(self, logger, db):
        self.db = db

    def find_for_offer_profile(self, offer_profile_id):
        return (self.db.query(BrandStyle)
                .filter(BrandStyle.offer_profile_id == offer_profile_id)
                .order_by(BrandStyle.id.desc()).all())

    def get_by_id(self, id):
        return self.db.get(BrandStyle, id)

    def create(self, item):
        try:
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
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

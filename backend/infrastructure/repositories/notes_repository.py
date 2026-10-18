from domain.models.context.note import Note
from domain.models.offer.offer_profile_note import OfferProfileNote


class NotesRepository:
    def __init__(self, logger, db):
        self.db = db

    def list_all(self):
        return self.db.query(Note).order_by(Note.title, Note.id).all()

    def get_by_id(self, note_id):
        return self.db.get(Note, note_id)

    def find_for_offer_profile(self, offer_profile_id):
        return (
            self.db.query(Note)
            .join(OfferProfileNote, OfferProfileNote.note_id == Note.id)
            .filter(OfferProfileNote.offer_profile_id == offer_profile_id)
            .order_by(Note.title, Note.id)
            .all()
        )

    def create_for_offer_profile(self, offer_profile_id, note):
        try:
            self.db.add(note)
            self.db.flush()
            self.db.add(OfferProfileNote(offer_profile_id=offer_profile_id, note_id=note.id))
            self.db.commit()
            self.db.refresh(note)
            return note
        except Exception:
            self.db.rollback()
            raise

    def create(self, note):
        try:
            self.db.add(note)
            self.db.commit()
            self.db.refresh(note)
            return note
        except Exception:
            self.db.rollback()
            raise

    def update(self, note):
        self.db.commit()
        self.db.refresh(note)
        return note

    def attach(self, offer_profile_id, note_id):
        if self.db.get(OfferProfileNote, (offer_profile_id, note_id)) is None:
            self.db.add(OfferProfileNote(offer_profile_id=offer_profile_id, note_id=note_id))
            self.db.commit()

    def detach(self, offer_profile_id, note_id):
        link = self.db.get(OfferProfileNote, (offer_profile_id, note_id))
        if link is not None:
            self.db.delete(link)
            self.db.commit()

    def delete(self, note):
        self.db.delete(note)
        self.db.commit()

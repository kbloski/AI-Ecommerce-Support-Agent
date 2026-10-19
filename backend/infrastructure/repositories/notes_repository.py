from domain.models.context.note import Note


class NotesRepository:
    def __init__(self, logger, db):
        self.db = db

    def list_all(self):
        return self.db.query(Note).order_by(Note.title, Note.id).all()

    def get_by_id(self, note_id):
        return self.db.get(Note, note_id)

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

    def delete(self, note):
        self.db.delete(note)
        self.db.commit()

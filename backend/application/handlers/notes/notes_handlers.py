from fastapi import HTTPException

from application.mappers.note_mapper import note_to_dict
from di.container import Container
from domain.models.context.note import Note


def _note(repository, note_id):
    note = repository.get_by_id(note_id)
    if note is None:
        raise HTTPException(404, "Note not found")
    return note


def list_notes_handler():
    return [note_to_dict(note) for note in Container().notes_repository().list_all()]


def create_note_handler(title, content):
    note = Note(title=title, content=content)
    return note_to_dict(Container().notes_repository().create(note))


def update_note_handler(note_id, title, content):
    repository = Container().notes_repository()
    note = _note(repository, note_id)
    note.title = title
    note.content = content
    return note_to_dict(repository.update(note))


def delete_note_handler(note_id):
    repository = Container().notes_repository()
    repository.delete(_note(repository, note_id))
    return {"deleted": True}

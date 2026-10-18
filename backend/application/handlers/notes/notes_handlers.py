from fastapi import HTTPException

from application.mappers.note_mapper import note_to_dict
from di.container import Container
from domain.models.context.note import Note


def _profile(container, offer_profile_id):
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")


def _note(repository, note_id):
    note = repository.get_by_id(note_id)
    if note is None:
        raise HTTPException(404, "Note not found")
    return note


def list_notes_handler(offer_profile_id=None):
    container = Container()
    repository = container.notes_repository()
    if offer_profile_id is None:
        notes = repository.list_all()
    else:
        _profile(container, offer_profile_id)
        notes = repository.find_for_offer_profile(offer_profile_id)
    return [note_to_dict(note) for note in notes]


def create_note_handler(title, content):
    note = Note(title=title, content=content)
    return note_to_dict(Container().notes_repository().create(note))


def create_profile_note_handler(offer_profile_id, title, content):
    container = Container()
    _profile(container, offer_profile_id)
    note = Note(title=title, content=content)
    return note_to_dict(container.notes_repository().create_for_offer_profile(offer_profile_id, note))


def update_note_handler(note_id, title, content):
    repository = Container().notes_repository()
    note = _note(repository, note_id)
    note.title = title
    note.content = content
    return note_to_dict(repository.update(note))


def attach_note_handler(offer_profile_id, note_id):
    container = Container()
    _profile(container, offer_profile_id)
    repository = container.notes_repository()
    _note(repository, note_id)
    repository.attach(offer_profile_id, note_id)
    return {"attached": True}


def detach_note_handler(offer_profile_id, note_id):
    container = Container()
    _profile(container, offer_profile_id)
    repository = container.notes_repository()
    _note(repository, note_id)
    repository.detach(offer_profile_id, note_id)
    return {"detached": True}


def delete_note_handler(note_id):
    repository = Container().notes_repository()
    repository.delete(_note(repository, note_id))
    return {"deleted": True}

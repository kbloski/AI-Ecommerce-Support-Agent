from fastapi import APIRouter, Path
from pydantic import BaseModel, ConfigDict, Field

from application.handlers.notes.notes_handlers import (
    attach_note_handler,
    create_note_handler,
    create_profile_note_handler,
    delete_note_handler,
    detach_note_handler,
    list_notes_handler,
    update_note_handler,
)


router = APIRouter()


class NoteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


@router.get("/notes")
def list_notes():
    return list_notes_handler()


@router.get("/offer-profiles/{offer_profile_id}/notes")
def list_profile_notes(offer_profile_id: int = Path(gt=0)):
    return list_notes_handler(offer_profile_id)


@router.post("/notes", status_code=201)
def create_note(payload: NoteRequest):
    return create_note_handler(payload.title, payload.content)


@router.post("/offer-profiles/{offer_profile_id}/notes", status_code=201)
def create_profile_note(payload: NoteRequest, offer_profile_id: int = Path(gt=0)):
    return create_profile_note_handler(offer_profile_id, payload.title, payload.content)


@router.post("/notes/{note_id}/update")
def update_note(payload: NoteRequest, note_id: int = Path(gt=0)):
    return update_note_handler(note_id, payload.title, payload.content)


@router.post("/offer-profiles/{offer_profile_id}/notes/{note_id}")
def attach_note(offer_profile_id: int = Path(gt=0), note_id: int = Path(gt=0)):
    return attach_note_handler(offer_profile_id, note_id)


@router.delete("/offer-profiles/{offer_profile_id}/notes/{note_id}")
def detach_note(offer_profile_id: int = Path(gt=0), note_id: int = Path(gt=0)):
    return detach_note_handler(offer_profile_id, note_id)


@router.delete("/notes/{note_id}")
def delete_note(note_id: int = Path(gt=0)):
    return delete_note_handler(note_id)

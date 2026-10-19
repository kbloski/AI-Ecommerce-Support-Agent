from fastapi import APIRouter, Path
from pydantic import BaseModel, ConfigDict, Field

from application.handlers.notes.notes_handlers import (
    create_note_handler,
    delete_note_handler,
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


@router.post("/notes", status_code=201)
def create_note(payload: NoteRequest):
    return create_note_handler(payload.title, payload.content)


@router.post("/notes/{note_id}/update")
def update_note(payload: NoteRequest, note_id: int = Path(gt=0)):
    return update_note_handler(note_id, payload.title, payload.content)


@router.delete("/notes/{note_id}")
def delete_note(note_id: int = Path(gt=0)):
    return delete_note_handler(note_id)

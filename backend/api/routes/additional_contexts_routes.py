from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field
from application.handlers.additional_contexts.list_additional_contexts_handler import list_additional_contexts_handler
from application.handlers.additional_contexts.create_additional_context_handler import create_additional_context_handler
from application.handlers.additional_contexts.update_additional_context_handler import update_additional_context_handler
from application.handlers.additional_contexts.attach_additional_context_handler import attach_additional_context_handler
from application.handlers.additional_contexts.detach_additional_context_handler import detach_additional_context_handler

router = APIRouter()

class ContextRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)

@router.get("/additional-contexts")
def list_contexts():
    return list_additional_contexts_handler()

@router.get("/offer-profiles/{id}/additional-contexts")
def list_profile_contexts(id: int):
    return list_additional_contexts_handler(id)

@router.post("/offer-profiles/{id}/additional-contexts", status_code=201)
def create_profile_context(id: int, payload: ContextRequest):
    return create_additional_context_handler(id, payload.name, payload.content)

@router.post("/additional-contexts/{id}/update")
def update_context(id: int, payload: ContextRequest):
    return update_additional_context_handler(id, payload.name, payload.content)

@router.post("/offer-profiles/{id}/additional-contexts/{context_id}")
def attach_context(id: int, context_id: int):
    return attach_additional_context_handler(id, context_id)

@router.delete("/offer-profiles/{id}/additional-contexts/{context_id}")
def detach_context(id: int, context_id: int):
    return detach_additional_context_handler(id, context_id)

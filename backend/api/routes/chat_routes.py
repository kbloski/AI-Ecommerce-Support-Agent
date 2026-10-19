from fastapi import APIRouter, Path
from fastapi.responses import Response

from application.dtos.chat.chat_fields import CreateConversationRequest, SendMessageRequest, UpdateConversationRequest
from application.handlers.chat.chat_handlers import (
    conversation_usage_handler, create_conversation_handler, delete_conversation_handler, get_conversation_handler,
    get_conversation_context_handler,
    delete_message_handler, edit_message_handler, fork_conversation_handler, regenerate_message_handler,
    update_message_handler,
    list_conversations_handler, send_message_handler, update_conversation_handler,
)

router = APIRouter()


@router.get("/chat/conversations")
def list_conversations():
    return list_conversations_handler()


@router.post("/chat/conversations", status_code=201)
def create_conversation(payload: CreateConversationRequest):
    return create_conversation_handler(payload)


@router.get("/chat/conversations/{id}")
def get_conversation(id: int = Path(gt=0)):
    return get_conversation_handler(id)


@router.get("/chat/conversations/{id}/usage")
def conversation_usage(id: int = Path(gt=0)):
    return conversation_usage_handler(id)


@router.get("/chat/conversations/{id}/context")
def conversation_context(id: int = Path(gt=0)):
    return Response(content=get_conversation_context_handler(id), media_type="text/plain; charset=utf-8")


@router.post("/chat/conversations/{id}/update")
def update_conversation(payload: UpdateConversationRequest, id: int = Path(gt=0)):
    return update_conversation_handler(id, payload)


@router.delete("/chat/conversations/{id}/delete")
def delete_conversation(id: int = Path(gt=0)):
    return delete_conversation_handler(id)


@router.post("/chat/conversations/{id}/messages")
def send_message(payload: SendMessageRequest, id: int = Path(gt=0)):
    return send_message_handler(id, payload)


@router.post("/chat/messages/{message_id}/fork", status_code=201)
def fork_conversation(message_id: int = Path(gt=0)):
    return fork_conversation_handler(message_id)


@router.post("/chat/messages/{message_id}/edit")
def edit_message(payload: SendMessageRequest, message_id: int = Path(gt=0)):
    return edit_message_handler(message_id, payload)


@router.post("/chat/messages/{message_id}/regenerate")
def regenerate_message(message_id: int = Path(gt=0)):
    return regenerate_message_handler(message_id)


@router.delete("/chat/messages/{message_id}/delete")
def delete_message(message_id: int = Path(gt=0)):
    return delete_message_handler(message_id)


@router.post("/chat/messages/{message_id}/update")
def update_message(payload: SendMessageRequest, message_id: int = Path(gt=0)):
    return update_message_handler(message_id, payload)

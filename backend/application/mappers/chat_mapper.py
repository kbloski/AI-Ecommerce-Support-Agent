def chat_message_to_dict(item):
    return {key: getattr(item, key) for key in ("id", "conversation_id", "role", "content", "prompt_tokens", "completion_tokens", "created_at")}


def chat_conversation_to_dict(item, messages=None):
    data = {key: getattr(item, key) for key in ("id", "title", "context", "created_at", "updated_at")}
    if messages is not None:
        data["messages"] = [chat_message_to_dict(message) for message in messages]
    return data

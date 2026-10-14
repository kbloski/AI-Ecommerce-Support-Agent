from typing import Any, Dict

from di.container import Container
from application.handlers.settings.get_ollama_settings_handler import get_ollama_settings_handler

ALLOWED_FIELDS = {"ollama_url", "ollama_model", "ollama_timeout", "ollama_context_length", "ollama_temperature"}


def save_ollama_settings_handler(fields: Dict[str, Any]):
    container = Container()
    repository = container.app_properties_repository()

    updates = {key: value for key, value in fields.items() if key in ALLOWED_FIELDS}
    repository.upsert(updates)

    return get_ollama_settings_handler()

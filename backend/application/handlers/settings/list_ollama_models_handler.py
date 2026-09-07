from typing import Optional

from fastapi import HTTPException
from ollama import Client

from di.container import Container


def list_ollama_models_handler(url: Optional[str] = None):
    container = Container()
    settings = container.settings()
    repository = container.app_ollama_settings_repository()

    overrides = repository.get()
    if url:
        host = url
    else:
        host = (overrides.ollama_url if overrides else None) or settings.get_ollama_url()

    timeout = (overrides.ollama_timeout if overrides else None) or settings.get_ollama_timeout()

    try:
        client = Client(host=host, timeout=timeout)
        response = client.list()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Nie udało się połączyć z Ollama pod adresem {host}: {e}",
        )

    return {
        "models": [model.model for model in response.models if model.model],
    }

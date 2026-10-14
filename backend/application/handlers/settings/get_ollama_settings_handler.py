from di.container import Container

FIELD_DEFAULT_GETTERS = {
    "ollama_url": "get_ollama_url",
    "ollama_model": "get_ollama_llm_model",
    "ollama_timeout": "get_ollama_timeout",
    "ollama_context_length": "get_ollama_num_ctx",
    "ollama_temperature": "get_ollama_temperature",
}


def get_ollama_settings_handler():
    container = Container()
    settings = container.settings()
    repository = container.app_properties_repository()

    overrides = repository.get()

    result = {}
    for field, getter_name in FIELD_DEFAULT_GETTERS.items():
        default_value = getattr(settings, getter_name)()
        override_value = getattr(overrides, field) if overrides else None
        result[field] = {
            "value": override_value if override_value is not None else default_value,
            "default": default_value,
            "is_override": override_value is not None,
        }

    return result

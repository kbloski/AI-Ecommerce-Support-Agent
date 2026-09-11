from ollama import Client
from infrastructure.logging.logger import Logger
from core.settings import Settings
from infrastructure.repositories.app_ollama_settings_repository import AppOllamaSettingsRepository

from domain.models.ollama.llm_ollama_message import LlmOllamaMessage
from domain.enums.ollama_message_role import OllamaMessageRole


def _with_fallback(value, fallback):
    return value if value is not None else fallback


class OllamaService:
    def __init__(self, logger: Logger, settings: Settings, app_ollama_settings_repository: AppOllamaSettingsRepository):
        self.logger = logger

        # Nadpisania per instancja aplikacji (baza danych) mają pierwszeństwo
        # przed wartościami domyślnymi z `.env`. Zob. memory/ai-ec-agent/architecture.md.
        overrides = app_ollama_settings_repository.get()

        self.llm_model = _with_fallback(overrides.ollama_model if overrides else None, settings.get_ollama_llm_model())
        self.num_ctx = _with_fallback(overrides.ollama_context_length if overrides else None, settings.get_ollama_num_ctx())
        self.temperature = _with_fallback(overrides.ollama_temperature if overrides else None, settings.get_ollama_temperature())
        self.timeout = _with_fallback(overrides.ollama_timeout if overrides else None, settings.get_ollama_timeout())
        host = _with_fallback(overrides.ollama_url if overrides else None, settings.get_ollama_url())

        self.client = Client(host=host, timeout=self.timeout)

    def chat_llm(
        self,
        messages: list[LlmOllamaMessage],
        *,
        json_response: bool = False,
        think: bool | None = None,
        num_predict: int | None = None,
    ) -> LlmOllamaMessage:
        """Obsługuje standardowe modele tekstowe (LLM)"""
        try:
            # ✅ Naprawione: Konwertujemy obiekty domenowe na słowniki akceptowane przez Ollamę
            payload_messages = [msg.to_dict() for msg in messages]

            options = {
                "num_ctx": self.num_ctx,
                "temperature": self.temperature,
            }
            if num_predict is not None:
                options["num_predict"] = num_predict

            response = self.client.chat(
                model=self.llm_model,
                messages=payload_messages,
                think=think,
                format="json" if json_response else None,
                options=options,
            )

            return LlmOllamaMessage(
                role=OllamaMessageRole.ASSISTANT,
                content=response["message"]["content"]
            )

        except Exception as e:
            self.logger.error(f"Ollama llm chat error: {e}")
            raise

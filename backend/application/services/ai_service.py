from infrastructure.logging.logger import Logger
from infrastructure.services.path_service import PathService
from application.services.ollama_service import OllamaService

from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole

from domain.models.ollama.llm_ollama_message import LlmOllamaMessage
from domain.enums.ollama_message_role import OllamaMessageRole

class AiService:
    def __init__(self, logger: Logger, path_service: PathService, ollama_service: OllamaService):
        self.logger = logger
        self.path_service = path_service
        self.ollama_service = ollama_service
        self.output_rules_prompt = self._load_prompt(self.path_service.OUTPUT_RULES_PROMPT)

    def _load_prompt(self, path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            self.logger.error(f"Nie udało się wczytać promptu {path}: {e}")
            return ""

    def chat_llm(
        self,
        messages: list[LlmMessage],
        *,
        json_response: bool = False,
        think: bool | None = None,
        num_predict: int | None = None,
    ) -> LlmMessage:
        self.output_rules_prompt = self._load_prompt(self.path_service.OUTPUT_RULES_PROMPT)

        payload_messages = list(messages)

        if self.output_rules_prompt:
            payload_messages.append(
                LlmMessage(
                    role=LlmMessageRole.SYSTEM,
                    content=self.output_rules_prompt
                )
            )

        ollama_messages = [
            LlmOllamaMessage(role=OllamaMessageRole(message.role.value), content=message.content)
            for message in payload_messages
        ]

        response = self.ollama_service.chat_llm(
            ollama_messages,
            json_response=json_response,
            think=think,
            num_predict=num_predict,
        )

        return LlmMessage(
            role=LlmMessageRole(response.role.value),
            content=response.content
        )

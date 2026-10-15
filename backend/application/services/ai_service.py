from collections.abc import Sequence

from application.services.llm_result_validation import parse_llm_json

from infrastructure.logging.logger import Logger
from infrastructure.services.path_service import PathService
from application.services.ollama_service import OllamaService

from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.enums.llm_rule_set import LlmRuleSet
from domain.models.ollama.llm_ollama_message import LlmOllamaMessage
from domain.enums.ollama_message_role import OllamaMessageRole


class AiService:
    def __init__(self, logger: Logger, path_service: PathService, ollama_service: OllamaService):
        self.logger = logger
        self.path_service = path_service
        self.ollama_service = ollama_service

    def chat_llm(
        self,
        messages: list[LlmMessage],
        *,
        json_response: bool = False,
        think: bool | None = None,
        num_predict: int | None = None,
        rule_sets: Sequence[LlmRuleSet] = (),
    ) -> LlmMessage:
        payload_messages = list(messages)

        for rule_set in dict.fromkeys(rule_sets):
            rules = self.path_service.rule_set_path(rule_set).read_text(encoding="utf-8").strip()
            if rules:
                payload_messages.append(LlmMessage(role=LlmMessageRole.SYSTEM, content=rules))

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
            content=response.content,
        )

    def chat_json(
        self,
        messages: list[LlmMessage],
        *,
        think: bool | None = None,
        num_predict: int | None = None,
        rule_sets: Sequence[LlmRuleSet] = (LlmRuleSet.ENGLISH_OUTPUT,),
    ) -> dict:
        """Request JSON from the model and return a parsed JSON object."""
        response = self.chat_llm(
            messages,
            json_response=True,
            think=think,
            num_predict=num_predict,
            rule_sets=(LlmRuleSet.JSON_OUTPUT, *rule_sets),
        )
        return parse_llm_json(response.content)

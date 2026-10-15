import unittest
from types import SimpleNamespace

from application.services.ai_service import AiService
from domain.enums.llm_message_role import LlmMessageRole
from domain.enums.llm_rule_set import LlmRuleSet
from domain.enums.ollama_message_role import OllamaMessageRole
from domain.models.llm.llm_message import LlmMessage
from domain.models.ollama.llm_ollama_message import LlmOllamaMessage
from infrastructure.services.path_service import PathService


class LlmRuleSetTests(unittest.TestCase):
    def test_rule_sets_are_explicit_and_independent(self):
        sent = []

        def chat(messages, **kwargs):
            sent.append(messages)
            return LlmOllamaMessage(role=OllamaMessageRole.ASSISTANT, content="{}")

        service = AiService(None, PathService(None), SimpleNamespace(chat_llm=chat))
        request = [LlmMessage(role=LlmMessageRole.USER, content="Generate an angle")]

        service.chat_llm(request)
        self.assertEqual(len(sent[-1]), 1)

        service.chat_llm(request, rule_sets=(LlmRuleSet.JSON_OUTPUT,))
        self.assertEqual(len(sent[-1]), 2)
        self.assertIn("valid JSON", sent[-1][-1].content)
        self.assertNotIn("Generate all textual content in English", sent[-1][-1].content)

        service.chat_llm(request, rule_sets=(LlmRuleSet.JSON_OUTPUT, LlmRuleSet.ENGLISH_OUTPUT, LlmRuleSet.JSON_OUTPUT))
        self.assertEqual(len(sent[-1]), 3)
        self.assertIn("valid JSON", sent[-1][1].content)
        self.assertIn("Generate all textual content in English", sent[-1][2].content)
        self.assertEqual(request[0].content, "Generate an angle")


if __name__ == "__main__":
    unittest.main()

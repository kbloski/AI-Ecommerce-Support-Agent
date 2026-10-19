from ...enums.ollama_message_role import OllamaMessageRole


class LlmOllamaMessage:
    def __init__(self, role: OllamaMessageRole, content: str, prompt_tokens: int | None = None, completion_tokens: int | None = None):
        self.role = role
        self.content = content
        # Exact token counts reported by Ollama for a response (prompt_eval_count / eval_count)
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

    def to_dict(self):
        return {
            "role": self.role.value,
            "content": self.content
        }

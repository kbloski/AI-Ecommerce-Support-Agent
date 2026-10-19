from ...enums.llm_message_role import LlmMessageRole


class LlmMessage:
    def __init__(self, role: LlmMessageRole, content: str, prompt_tokens: int | None = None, completion_tokens: int | None = None):
        self.role = role
        self.content = content
        # Exact token counts reported by the model for a response, when available
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

    def to_dict(self):
        return {
            "role": self.role.value,
            "content": self.content
        }

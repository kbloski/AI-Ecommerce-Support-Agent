from enum import Enum


class LlmRuleSet(str, Enum):
    JSON_OUTPUT = "json_output"
    ENGLISH_OUTPUT = "english_output"

from di.container import Container
from domain.enums.llm_rule_set import LlmRuleSet


def save_rule_set_handler(rule_set: LlmRuleSet, content: str):
    path = Container().path_service().rule_set_path(rule_set)
    path.write_text(content, encoding="utf-8")
    return {"rule_set": rule_set.value, "content": content}

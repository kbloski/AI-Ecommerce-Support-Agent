from di.container import Container
from domain.enums.llm_rule_set import LlmRuleSet


def get_rule_set_handler(rule_set: LlmRuleSet):
    path = Container().path_service().rule_set_path(rule_set)
    return {"rule_set": rule_set.value, "content": path.read_text(encoding="utf-8")}

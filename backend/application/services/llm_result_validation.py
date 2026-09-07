import json
from typing import Any


class LlmGenerationError(Exception):
    """Raised when an LLM response is missing, malformed, or fails structural
    validation. Handlers raise this instead of returning an ad-hoc error dict,
    so routes can translate it into a proper HTTP error status."""

    def __init__(self, message: str, raw_response: str | None = None):
        super().__init__(message)
        self.message = message
        self.raw_response = raw_response


def parse_llm_json(raw_content: str | None) -> dict:
    """Parses the raw LLM response text into a JSON object, stripping an
    optional ```/```json code fence. Raises LlmGenerationError on anything
    that isn't a valid JSON object."""
    if not isinstance(raw_content, str) or not raw_content.strip():
        raise LlmGenerationError("LLM returned empty response", raw_response=raw_content)

    content = raw_content.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise LlmGenerationError(f"Invalid JSON response: {e}", raw_response=raw_content) from e

    if not isinstance(result, dict):
        raise LlmGenerationError("Root JSON value must be an object", raw_response=raw_content)

    return result


def require_dict(value: Any, field_name: str, raw_response: str | None = None) -> dict:
    if not isinstance(value, dict):
        raise LlmGenerationError(f"'{field_name}' must be an object", raw_response=raw_response)
    return value


def require_list(value: Any, field_name: str, raw_response: str | None = None) -> list:
    if not isinstance(value, list):
        raise LlmGenerationError(f"'{field_name}' must be a list", raw_response=raw_response)
    return value


def validate_ordered_sections(
    sections: list,
    *,
    allowed_section_types: set[str] | None,
    allowed_priorities: set[str],
    raw_response: str | None = None,
) -> None:
    """Shared structural checks for both page_blueprint and page_copy sections:
    every entry is an object with a valid section_type, order values are
    sequential starting at 1 with no duplicates or gaps."""
    if not sections:
        raise LlmGenerationError("Sections list must not be empty", raw_response=raw_response)

    orders = []
    for index, section in enumerate(sections):
        require_dict(section, f"sections[{index}]", raw_response=raw_response)

        section_type = section.get("section_type")
        if not section_type or not isinstance(section_type, str):
            raise LlmGenerationError(f"sections[{index}].section_type is required", raw_response=raw_response)
        if allowed_section_types is not None and section_type not in allowed_section_types:
            raise LlmGenerationError(
                f"sections[{index}].section_type '{section_type}' is not a known page section type",
                raw_response=raw_response,
            )

        priority = section.get("section_priority")
        if priority is not None:
            if priority not in allowed_priorities:
                raise LlmGenerationError(
                    f"sections[{index}].section_priority '{priority}' is invalid", raw_response=raw_response
                )

        order = section.get("order")
        if not isinstance(order, int) or isinstance(order, bool):
            raise LlmGenerationError(f"sections[{index}].order must be an integer", raw_response=raw_response)
        orders.append(order)

    if sorted(orders) != list(range(1, len(orders) + 1)):
        raise LlmGenerationError(
            "sections[].order must be sequential starting at 1 with no duplicates or gaps",
            raw_response=raw_response,
        )

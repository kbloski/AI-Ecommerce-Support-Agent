import json
from typing import Any

from di.container import Container
from domain.enums.enums import CreativeTypes
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.creative_execution_setup.creative_execution_setup import CreativeExecutionSetup
from domain.models.llm.llm_message import LlmMessage


def generate_creative_execution_setups_handler(ad_setup_id: int, count: int):
    container = Container()
    ad_setup_service = container.ad_setup_service()
    creative_strategy_service = container.creative_strategy_service()
    ad_strategy_service = container.ad_strategy_service()
    repository = container.creative_execution_setup_repository()
    setup_service = container.creative_execution_setup_service()

    ad_setup = ad_setup_service.get_ad_setup_by_id(ad_setup_id)
    creative_strategy = creative_strategy_service.get_creative_strategy_by_id(
        ad_setup.creative_strategy_id
    )
    ad_strategy = ad_strategy_service.get_ad_strategy_by_id(
        creative_strategy.ad_strategy_id
    )

    frameworks = [
        item.to_dict()
        for item in container.ad_frameworks_repository().get_all()
        if item.format == ad_setup.creative_type
    ]
    angles = [item.to_dict() for item in container.creative_angels_repository().get_all()]
    styles = [item.to_dict() for item in container.execution_styles_repository().get_all()]
    existing = setup_service.list_for_ad_setup(ad_setup_id)

    response = container.ai_service().chat_llm(
        messages=[
            LlmMessage(role=LlmMessageRole.SYSTEM, content=get_system_prompt()),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=get_data_prompt(
                    count=count,
                    creative_type=ad_setup.creative_type,
                    ad_strategy_context=ad_strategy_service.build_llm_context(ad_strategy.id),
                    creative_strategy_context=creative_strategy_service.build_llm_context(creative_strategy.id),
                    ad_setup_context=ad_setup_service.build_llm_context(ad_setup.id),
                    frameworks=frameworks,
                    angles=angles,
                    styles=styles,
                    existing=[_deduplication_payload(item) for item in existing],
                ),
            ),
        ]
    )

    result = _parse_llm_json(response.content)
    payloads = _validate_payload(
        result=result,
        count=count,
        creative_type=ad_setup.creative_type,
        frameworks=frameworks,
        angles=angles,
        styles=styles,
        existing=existing,
    )

    entities = [CreativeExecutionSetup(ad_setup_id=ad_setup_id, **payload) for payload in payloads]
    created = repository.create_many(entities)
    return [setup_service.get_by_id(item.id) for item in created]


def _parse_llm_json(content: str) -> dict[str, Any]:
    raw = content.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM returned invalid JSON for Creative Execution Setups") from exc

    if not isinstance(result, dict):
        raise ValueError("Creative Execution Setup response must be a JSON object")
    return result


def _validate_payload(
    result: dict[str, Any],
    count: int,
    creative_type: str,
    frameworks: list[dict[str, Any]],
    angles: list[dict[str, Any]],
    styles: list[dict[str, Any]],
    existing: list,
) -> list[dict[str, Any]]:
    items = result.get("creative_execution_setups")
    if not isinstance(items, list) or len(items) != count:
        raise ValueError(f"LLM must return exactly {count} Creative Execution Setups")

    framework_ids = {item["id"] for item in frameworks}
    angle_ids = {item["id"] for item in angles}
    style_ids = {item["id"] for item in styles}
    used_keys = {_configuration_key(_deduplication_payload(item)) for item in existing}
    validated = []

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Creative Execution Setup #{index} must be an object")

        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Creative Execution Setup #{index} must have a name")
        name = name.strip()
        if len(name) > 255:
            raise ValueError(f"Creative Execution Setup #{index} name is too long")

        framework_id = item.get("ad_framework_id")
        angle_id = item.get("creative_angle_id")
        style_id = item.get("execution_style_id")

        if framework_ids and framework_id not in framework_ids:
            raise ValueError(f"Creative Execution Setup #{index} has an unsupported ad framework")
        if not framework_ids and framework_id is not None:
            raise ValueError(f"Creative Execution Setup #{index} must not select an incompatible ad framework")
        if angle_id not in angle_ids:
            raise ValueError(f"Creative Execution Setup #{index} has an unsupported creative angle")
        if style_id not in style_ids:
            raise ValueError(f"Creative Execution Setup #{index} has an unsupported execution style")

        duration = item.get("duration_seconds")
        slides = item.get("number_of_slides")
        if creative_type == CreativeTypes.VIDEO.value:
            if isinstance(duration, bool) or not isinstance(duration, int) or not 5 <= duration <= 120:
                raise ValueError(f"Creative Execution Setup #{index} duration must be between 5 and 120 seconds")
            slides = None
        elif creative_type == CreativeTypes.CAROUSEL.value:
            if isinstance(slides, bool) or not isinstance(slides, int) or not 2 <= slides <= 20:
                raise ValueError(f"Creative Execution Setup #{index} slide count must be between 2 and 20")
            duration = None
        elif creative_type == CreativeTypes.IMAGE.value:
            duration = None
            slides = None
        else:
            raise ValueError(f"Unsupported creative type: {creative_type}")

        instructions = item.get("additional_instructions")
        if instructions is not None and not isinstance(instructions, str):
            raise ValueError(f"Creative Execution Setup #{index} additional instructions must be text")

        payload = {
            "name": name,
            "duration_seconds": duration,
            "number_of_slides": slides,
            "ad_framework_id": framework_id,
            "creative_angle_id": angle_id,
            "execution_style_id": style_id,
            "additional_instructions": instructions.strip() if instructions else None,
        }
        key = _configuration_key(payload)
        if key in used_keys:
            raise ValueError(f"Creative Execution Setup #{index} duplicates an existing or generated configuration")
        used_keys.add(key)
        validated.append(payload)

    return validated


def _deduplication_payload(item) -> dict[str, Any]:
    return {
        "ad_framework_id": item.ad_framework_id,
        "creative_angle_id": item.creative_angle_id,
        "execution_style_id": item.execution_style_id,
        "duration_seconds": item.duration_seconds,
        "number_of_slides": item.number_of_slides,
    }


def _configuration_key(item: dict[str, Any]) -> tuple:
    return (
        item.get("ad_framework_id"),
        item.get("creative_angle_id"),
        item.get("execution_style_id"),
        item.get("duration_seconds"),
        item.get("number_of_slides"),
    )


def get_system_prompt() -> str:
    return """
You are a senior performance creative planner.

Create execution configurations, not finished advertisements and not new strategies.
AD STRATEGY defines the advertising direction. CREATIVE STRATEGY defines the selected
idea, message angle, hook direction and emotional flow. AD SETUP defines the medium,
platform and format. Preserve all three sources and only choose a strong way to execute them.

Use only IDs present in the supplied catalogs. Configurations must be meaningfully distinct,
not renamed copies. Never invent product facts, claims, prices, proof, guarantees or results.
Additional instructions may describe production and presentation choices only.

Return valid JSON only, with this exact structure:
{
  "creative_execution_setups": [
    {
      "name": "",
      "duration_seconds": null,
      "number_of_slides": null,
      "ad_framework_id": null,
      "creative_angle_id": "",
      "execution_style_id": "",
      "additional_instructions": ""
    }
  ]
}
"""


def get_data_prompt(
    count: int,
    creative_type: str,
    ad_strategy_context: str,
    creative_strategy_context: str,
    ad_setup_context: str,
    frameworks: list[dict[str, Any]],
    angles: list[dict[str, Any]],
    styles: list[dict[str, Any]],
    existing: list[dict[str, Any]],
) -> str:
    return f"""
Generate exactly {count} new and mutually distinct Creative Execution Setups.

CREATIVE TYPE: {creative_type}

AD STRATEGY:
{ad_strategy_context}

CREATIVE STRATEGY:
{creative_strategy_context}

AD SETUP:
{ad_setup_context}

ALLOWED AD FRAMEWORKS COMPATIBLE WITH THIS MEDIUM:
{json.dumps(frameworks, ensure_ascii=False, indent=2)}

ALLOWED CREATIVE ANGLES:
{json.dumps(angles, ensure_ascii=False, indent=2)}

ALLOWED EXECUTION STYLES:
{json.dumps(styles, ensure_ascii=False, indent=2)}

EXISTING CONFIGURATIONS — DO NOT DUPLICATE THESE COMBINATIONS:
{json.dumps(existing, ensure_ascii=False, indent=2)}

Rules for medium-specific fields:
- video: duration_seconds must be an integer from 5 to 120; number_of_slides must be null;
- carousel: number_of_slides must be an integer from 2 to 20; duration_seconds must be null;
- image: both fields must be null;
- when the compatible framework catalog is empty, ad_framework_id must be null;
- otherwise ad_framework_id must be selected from that catalog;
- creative_angle_id and execution_style_id are required and must use catalog IDs.

Return exactly {count} items and only the JSON object.
"""

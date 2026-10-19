import json

from fastapi import HTTPException
from pydantic import ValidationError

from application.dtos.page_blueprint.page_blueprint_fields import (
    GeneratePageBlueprintRequest, PageBlueprintFields, PageBlueprintGenerationResponse,
)
from application.handlers.page_blueprint.create_page_blueprint_handler import create_page_blueprint_handler
from application.services.llm_context_composer import ContextRef, ContextSelection
from application.services.llm_result_validation import LlmGenerationError, parse_llm_json
from di.container import Container
from domain.enums.context_type import ContextType
from domain.enums.llm_message_role import LlmMessageRole
from domain.enums.page_type import PageType
from domain.models.llm.llm_message import LlmMessage


def generate_page_blueprint_handler(offer_profile_id: int, request: GeneratePageBlueprintRequest | None = None):
    request = request or GeneratePageBlueprintRequest()
    container = Container()
    try:
        context = container.llm_context_composer().compose(
            root=ContextRef(ContextType.OFFER_PROFILE, offer_profile_id),
            include=[ContextSelection(ContextType.OFFER_SOURCE)],
        )
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    prompt_data = {
        "offer_context": context,
        "page_type": request.page_type.value if request.page_type is not None else None,
        "requested_section_count": request.section_count,
        "generation_instructions": request.generation_instructions.strip(),
    }
    if request.page_type is PageType.PRODUCT_PAGE:
        prompt_data["section_suggestions"] = container.page_sections_service().get_all_for_blueprints()
    
    response = container.ai_service().chat_llm(messages=[
        LlmMessage(role=LlmMessageRole.SYSTEM, content=_get_system_prompt()),
        LlmMessage(role=LlmMessageRole.USER, content=json.dumps(prompt_data, ensure_ascii=False, indent=2)),
    ])
    fields = _parse_and_validate(response.content, request.section_count)
    return create_page_blueprint_handler(
        offer_profile_id=offer_profile_id, name=fields.name, description=fields.description,
        sections=[section.model_dump() for section in fields.sections],
    )


def _parse_and_validate(content: str, section_count: int | None) -> PageBlueprintFields:
    try:
        generated = PageBlueprintGenerationResponse.model_validate(parse_llm_json(content))
        fields = PageBlueprintFields.model_validate(generated.model_dump())
        if section_count is not None and len(fields.sections) != section_count:
            raise ValueError(f"Expected exactly {section_count} sections, received {len(fields.sections)}")
        return fields
    except (ValidationError, ValueError) as error:
        raise LlmGenerationError(f"Invalid Page Blueprint response: {error}", raw_response=content) from error



def _get_system_prompt() -> str:
    return """
You are a senior website information architect and digital
experience strategist specializing in page structure,
content hierarchy, user journeys and conversion strategy.

Your task is to design exactly ONE PAGE BLUEPRINT
tailored to the supplied OFFER PROFILE.
Use page_type to shape the page objective and structure.
If page_type is null, infer a suitable structure from the offer
and generation_instructions. Do not assume a product page by default.
product_page presents a product.

A page blueprint defines WHAT sections a page needs,
WHY they exist and HOW they should be sequenced.
It is not final copy, a visual design or a rigid template.

DESIGN PRINCIPLES:
- Understand the offer, target audience, user intent
  and primary page objective before choosing sections.
- Build a coherent narrative that guides visitors
  from initial interest toward the intended action.
- Prioritize relevance, clarity and meaningful content
  over conventional landing page patterns.
- Every section must serve a distinct purpose.
- Avoid redundant, generic or filler sections.
- Adapt the structure to the offer rather than
  forcing the offer into a predefined layout.
- Consider credibility, objections and decision-making
  needs only when relevant and factually supported.
- Do not invent facts, testimonials, pricing, results,
  guarantees, urgency or unsupported claims.

SECTION SELECTION:
- section_suggestions, when present, is an optional inspiration catalog,
  not a checklist, enum or required structure.
- You may omit, combine or repeat suggested section types.
- You may create custom descriptive section types.
- Repeated types should serve distinct purposes.
- Choose sections based on the offer and page objective,
  not merely because they appear in the catalog.
- Follow generation_instructions within factual constraints.

SECTION COUNT:
- Generate exactly ONE page blueprint.
- If requested_section_count is specified, return
  exactly that many sections.
- Otherwise, choose an appropriate count (1–50).
- Every section, including optional ones, counts.

OUTPUT REQUIREMENTS:
Each section must contain:
- type: concise descriptive section category;
- name: specific, meaningful section name;
- purpose: what the section should communicate or achieve;
- position: unique integer, sequentially starting at 1;
- is_optional: whether the section can be omitted
  without compromising the page's core objective.

Do not include database IDs.

Return valid JSON only, with no markdown or extra fields:

{
  "name": "Distinctive blueprint name",
  "description": "Brief explanation of the page strategy",
  "sections": [
    {
      "type": "hero",
      "name": "Core value proposition",
      "purpose": "Establish immediate relevance and explain the offer",
      "position": 1,
      "is_optional": false
    }
  ]
}
""".strip()

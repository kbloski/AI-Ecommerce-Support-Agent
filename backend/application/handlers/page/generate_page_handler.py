import json

from fastapi import HTTPException
from pydantic import ValidationError

from application.dtos.page.page_fields import GeneratePageRequest, GeneratedPage
from application.services.llm_context_composer import ContextRef, ContextSelection
from application.services.llm_result_validation import LlmGenerationError, parse_llm_json
from di.container import Container
from domain.enums.context_type import ContextType
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.llm.llm_message import LlmMessage
from domain.models.page.page import Page
from domain.models.page.page_section import PageSection
from infrastructure.database.unit_of_work import unit_of_work


def generate_page_handler(offer_profile_id: int, request: GeneratePageRequest):
    container = Container()
    try:
        offer_context = container.llm_context_composer().compose(
            root=ContextRef(ContextType.OFFER_PROFILE, offer_profile_id),
            include=[ContextSelection(ContextType.OFFER_SOURCE)],
        )
    except LookupError as error:
        raise HTTPException(404, str(error)) from error

    blueprint = None
    if request.page_blueprint_id is not None:
        try:
            blueprint = container.page_blueprint_service().get_page_blueprint_by_id(request.page_blueprint_id)
        except LookupError as error:
            raise HTTPException(404, str(error)) from error
        if blueprint.offer_profile_id != offer_profile_id:
            raise HTTPException(422, "Page blueprint must belong to this offer profile")

    prompt_data = {
        "offer_context": offer_context,
        "generation_instructions": request.generation_instructions.strip(),
    }
    if blueprint is not None:
        prompt_data["page_blueprint"] = blueprint.to_content_dict()
    response = container.ai_service().chat_llm(messages=[
        LlmMessage(role=LlmMessageRole.SYSTEM, content=_system_prompt()),
        LlmMessage(role=LlmMessageRole.USER, content=json.dumps(prompt_data, ensure_ascii=False, indent=2)),
    ])
    generated = _validate_response(response.content, blueprint)
    with unit_of_work(container.db()):
        page = container.page_repository().create(
            Page(offer_profile_id=offer_profile_id, page_blueprint_id=request.page_blueprint_id,
                 name=generated.name, description=generated.description),
            [PageSection(**section.model_dump()) for section in generated.sections],
        )
    return container.page_service().get_by_id(page.id)


def _validate_response(content: str, blueprint) -> GeneratedPage:
    try:
        generated = GeneratedPage.model_validate(parse_llm_json(content))
        if blueprint is not None:
            expected = [section["type"] for section in sorted(blueprint.sections, key=lambda item: item["position"])]
            actual = [section.type for section in sorted(generated.sections, key=lambda item: item.position)]
            if actual != expected:
                raise ValueError("Generated sections must match the selected blueprint types and order")
        return generated
    except (ValidationError, ValueError) as error:
        raise LlmGenerationError(f"Invalid Page response: {error}", raw_response=content) from error


def _system_prompt() -> str:
    return """
Create exactly ONE page draft for the supplied offer. Write usable page copy,
not a blueprint, code, HTML, or a visual design. Use the offer context and
generation_instructions. Do not invent product capabilities, prices, discounts,
customer proof, guarantees, deadlines, outcomes, or other unsupported facts.
When facts needed for a claim are missing, use restrained wording or omit it.

If page_blueprint is provided, follow every section in its exact position and
type order, including optional sections. Use each section's name and purpose
to guide its heading and copy. Repeated types represent separate sections.
If no blueprint is provided, choose a coherent set of 1 to 50 sections.

Return JSON only, with no markdown or additional fields:
{
  "name": "Page name",
  "description": "Brief page intent",
  "sections": [
    {"type": "hero", "name": "Section heading", "content": "Page-ready section copy", "position": 1}
  ]
}
Each section needs a distinct purpose, a heading, and substantive copy.
Positions must be unique integers from 1 through the number of sections.
""".strip()

import json

from di.container import Container

from domain.models.llm.llm_message import LlmMessage
from domain.models.offer_profiles.offer_profile_element import OfferProfileElement

from domain.enums.llm_message_role import LlmMessageRole
from domain.enums.offer_profile_element_type import OfferProfileElementType

from application.services.llm_context_builder import build_llm_section
from application.mappers.offer_profile_element_mapper import OfferProfileElementMapper


# =====================================================
# MAIN HANDLER
# =====================================================

def generate_offer_profile_elements_handler(
    offer_profile_id: int,
    element_types: list[OfferProfileElementType],
    examples_per_type: int = 3,
) -> list[dict]:

    container = Container()

    offer_profile_service = container.offer_profile_service()
    offer_profile_elements_repository = container.offer_profile_elements_repository()
    ai_service = container.ai_service()

    # ----------------------------
    # LOAD OFFER PROFILE CONTEXT
    # ----------------------------

    offer_profile_context = offer_profile_service.build_llm_context(
        offer_profile_id=offer_profile_id
    )

    # ----------------------------
    # GENERATE OFFER ELEMENTS
    # ----------------------------

    chat = [
        LlmMessage(
            role=LlmMessageRole.SYSTEM,
            content=get_system_prompt(),
        ),
        LlmMessage(
            role=LlmMessageRole.USER,
            content=get_offer_elements_generation_prompt(
                offer_profile_context=offer_profile_context,
                element_types=element_types,
                examples_per_type=examples_per_type,
            ),
        ),
    ]

    response = ai_service.chat_llm(chat).content

    json_data = json.loads(response)

    # ----------------------------
    # SAVE TO DATABASE
    # ----------------------------

    created_elements = []

    for element_data in json_data.get("offer_elements", []):

        if not isinstance(element_data, dict):
            continue

        try:
            element_type = OfferProfileElementType(element_data.get("type"))
        except (TypeError, ValueError):
            continue

        if element_type not in element_types:
            continue

        name = str(element_data.get("name", "")).strip()

        if not name:
            continue

        description = str(element_data.get("description", "")).strip() or None

        element = OfferProfileElement(
            offer_profile_id=offer_profile_id,
            type=element_type,
            name=name,
            description=description,
        )

        created_elements.append(
            offer_profile_elements_repository.create(element)
        )

    # Group by type (stable sort by type, then name) — matches how
    # OfferProfileElementsRepository.find_for_offer_profile orders results.
    created_elements.sort(
        key=lambda element: (str(element.type), element.name)
    )

    return [OfferProfileElementMapper.to_dto(element).to_dict() for element in created_elements]


# =====================================================
# SYSTEM PROMPT
# =====================================================

def get_system_prompt() -> str:
    return """
You are a senior product strategist AI specialized in product analysis,
market research, customer psychology, and marketing strategy.

Your role is to analyze an existing offer profile and extract structured
offer elements for the requested element types.

Return ONLY valid JSON.
Do not use markdown.
"""


# =====================================================
# OFFER ELEMENTS GENERATION PROMPT
# =====================================================

def get_offer_elements_generation_prompt(
    offer_profile_context: str,
    element_types: list[OfferProfileElementType],
    examples_per_type: int,
) -> str:

    element_types_context = build_offer_element_types_context(
        element_types=element_types
    )

    expected_total = len(element_types) * examples_per_type

    return f"""
Analyze the offer profile and generate structured offer elements
for the requested element types.

Your task is NOT to regenerate or modify the whole offer profile.

Your task is ONLY to discover and generate OfferProfileElements
for the selected element types.


OFFER PROFILE:

{offer_profile_context}


SELECTED ELEMENT TYPES:

{element_types_context}


GENERATION PROCESS:

For EACH selected element type:

1. Understand the semantic meaning of the type using its definition.
2. Analyze the offer specifically from the perspective of that type.
3. Identify meaningful elements that are directly supported by
   the offer or can reasonably be derived from it.
4. Generate exactly {examples_per_type} distinct elements for that type.
5. Continue independently with the next selected type.


GENERATION COUNT:

- Generate exactly {examples_per_type} elements for EACH selected element type.
- There are {len(element_types)} selected element types.
- The final "offer_elements" array should contain exactly {expected_total} elements.
- Each selected type should appear exactly {examples_per_type} times.


IMPORTANT TYPE RULES:

- Generate ONLY the element types listed in SELECTED ELEMENT TYPES.
- Never generate another type.
- Treat each selected type as a separate analytical perspective.
- Do not confuse one type with another.
- A feature describes what the offer has or does.
- A benefit describes what the customer gains.
- A problem_solved describes the problem that exists before the solution.
- A use_case describes a concrete usage scenario.
- A differentiator describes meaningful distinction from alternatives.
- A limitation describes a meaningful restriction, boundary or trade-off.


CONTENT RULES:

- Stay specific to the analyzed offer.
- Avoid generic business statements.
- Prefer concrete insights over broad statements.
- Generate exactly {examples_per_type} elements for every selected type.
- Use reasonable inferences from the offer when needed, but do not invent facts.
- Multiple elements may have the same type.
- Avoid semantic duplicates.
- Do not repeat the same insight using slightly different wording.


FACT AND ASSUMPTION RULES:

- Prefer facts supported by the offer.
- Reasonable inference is allowed when necessary.
- Do not invent unsupported product functionality.
- Do not invent unsupported claims.
- Do not invent competitive advantages.
- If an element significantly depends on an assumption,
  make that clear in its description.


FIELD RULES:

"type":
- MUST contain one of the values from SELECTED ELEMENT TYPES.
- MUST be a single string.

"name":
- Short and specific.
- Clearly describes the element.
- Avoid vague names.

"description":
- Explain what the element means specifically for this offer.
- Provide enough context for another AI system to understand and use
  the element later.
- Do not write advertising copy.


OUTPUT SCHEMA:

{{
    "offer_elements": [
        {{
            "type": "",
            "name": "",
            "description": ""
        }}
    ]
}}


Return ONLY valid JSON.
Do not include explanations outside the JSON.
"""


# =====================================================
# OFFER ELEMENT TYPES CONTEXT
# =====================================================

OFFER_PROFILE_ELEMENT_TYPE_DEFINITIONS: dict[
    OfferProfileElementType,
    str,
] = {
    OfferProfileElementType.BENEFIT:
        "What the customer gains from the offer.",

    OfferProfileElementType.FEATURE:
        "What the offer has or does.",

    OfferProfileElementType.PROBLEM_SOLVED:
        "The problem that exists before the solution is applied.",

    OfferProfileElementType.USE_CASE:
        "A concrete usage scenario for the offer.",

    OfferProfileElementType.DIFFERENTIATOR:
        "A meaningful distinction from alternatives.",

    OfferProfileElementType.LIMITATION:
        "A meaningful restriction, boundary, or trade-off of the offer.",
}


def build_offer_element_types_context(
    element_types: list[OfferProfileElementType],
) -> str:

    definitions = [
        {
            "type": element_type.value,
            "definition": OFFER_PROFILE_ELEMENT_TYPE_DEFINITIONS[element_type],
        }
        for element_type in element_types
    ]

    return build_llm_section(
        tag="offer_element_types",
        content=json.dumps(
            definitions,
            ensure_ascii=False,
            indent=2,
        ),
    )

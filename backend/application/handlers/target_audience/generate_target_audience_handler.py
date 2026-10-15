import json
from typing import Dict, Any

from fastapi import HTTPException

from di.container import Container
from application.mappers.target_audience_mapper import TargetAudienceMapper

from domain.models.llm.llm_message import LlmMessage
from domain.models.audience.target_audience import TargetAudience

from domain.enums.llm_message_role import LlmMessageRole
from domain.enums.genders import Genders
from domain.enums.fact_status import FactStatus

def generate_target_audience_handler(
    offer_profile_id: int,
    count: int = 3,
    generation_instructions: str = "",
) -> Dict[str, Any]:
    if not 1 <= count <= 10:
        raise HTTPException(422, "Count must be between 1 and 10")
    container = Container()

    target_audience_repo = container.target_audiences_repository()

    ai_service = container.ai_service()
    offer_profile_service = container.offer_profile_service()
    try:
        offer_profile_context = offer_profile_service.build_llm_context(offer_profile_id=offer_profile_id)
    except LookupError as error:
        raise HTTPException(404, str(error)) from error

    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt()
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=get_target_audience_prompt(
                    offer_profile_context=offer_profile_context,
                    count=count,
                    generation_instructions=generation_instructions,
                )
            )
        ]
    )

    response_json = json.loads(response.content )
    audiences_arr = response_json["audiences"]
    if len(audiences_arr) != count:
        raise HTTPException(502, f"Expected {count} target audiences, received {len(audiences_arr)}")

    new_target_audiences = []
    for t in audiences_arr:
        new_target_audiences.append(
            TargetAudience(
                offer_profile_id=offer_profile_id,
                fact_status=FactStatus.UNVERIFIED.value,
                name=t["name"],
                age_min=t["age_min"],
                age_max=t["age_max"],
                gender=t["gender"],
                lifestyles=t["lifestyles"],
                values=t["values"],
                pain_points=t["pain_points"],
                motivations=t["motivations"],
                buying_triggers=t["buying_triggers"],
                desires=t["desires"],
            )
        )

    target_audience_repo.create_many(items=new_target_audiences)

    return new_target_audiences



def get_system_prompt() -> str:
    return """
You are a senior AI product strategy specialist specializing in:

- customer segmentation,
- buying psychology,
- market research,
- ICP (Ideal Customer Profile) definition,
- marketing strategy,
- conversion optimization.

You transform the supplied offer profile into practical customer segments.

Your goal is to determine:

1. Who is most likely to buy the product.
2. Why they will buy it.

Rules:
- Ground every segment in the supplied profile and attached information.
- Do not create generic customer groups.
- Do not invent product capabilities or unsupported demographic details.
- If data is missing, use null for demographics and empty arrays for list fields.
- Make segments meaningfully different in needs, motivations, or buying triggers.
- Results must be useful for advertising and marketing.

Desires describe what the audience wants; motivations describe why they act.
Return ONLY valid JSON.
"""


def get_target_audience_schema() -> str:
    return json.dumps({"audiences": [{
        "name": "",
        "age_min": None,
        "age_max": None,
        "gender": None,
        "lifestyles": [],
        "values": [],
        "pain_points": [],
        "desires": [],
        "motivations": [],
        "buying_triggers": [],
    }]}, ensure_ascii=False, indent=2)


def _enum_values(enum_cls) -> str:
    return ", ".join(member.value for member in enum_cls)


def get_enums_prompt() -> str:
    return f"""
Allowed enum values:

gender:
Genders:
{_enum_values(Genders)}

Enum rules:

- Enum fields must contain a single allowed string value or null when unknown.
- Do not return arrays.
- Do not create new values.
- Use only values available in the corresponding enum.

Correct example:

"gender": "all"

Incorrect example:

"gender": ["male", "female"]
"""


def get_target_audience_prompt(
    offer_profile_context: str,
    count: int = 3,
    generation_instructions: str = "",
) -> str:
    user_guidance = generation_instructions.strip()
    instructions_section = (
        f"\nUSER GENERATION INSTRUCTIONS:\n{user_guidance}\n"
        if user_guidance else ""
    )
    return f"""
Analyze the offer profile and its attached additional information.

OFFER PROFILE CONTEXT:

{offer_profile_context}

{instructions_section}

Generate exactly {count} target audience segments for this specific offer profile.
Use its name and attached additional information to define its perspective.
Use only information included in the profile context; do not invent product capabilities.
Apply the user's generation instructions where they fit the profile and required response format.
Give each segment a distinct buying situation, need, or motivation. Avoid overlapping names and repeated list entries.
Write the segments in the language of the profile context.


Response format:

{get_target_audience_schema()}


ENUM RULES:

{get_enums_prompt()}


Requirements:
- Return exactly {count} distinct target audience segments in the audiences array.
- Use null for age or gender when the context does not support a specific value.
- Use empty arrays when the context does not support a list value.
- Keep every field specific, concise, and grounded in the context.
- JSON ONLY.
"""

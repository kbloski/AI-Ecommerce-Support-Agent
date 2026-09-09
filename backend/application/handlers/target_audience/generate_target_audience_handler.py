import json
from typing import Dict, Any

from di.container import Container
from application.mappers.offer_profile_mapper import OfferProfileMapper
from application.mappers.target_audience_mapper import TargetAudienceMapper

from domain.models.llm.llm_message import LlmMessage
from domain.models.audience.target_audience import TargetAudience

from domain.enums.llm_message_role import LlmMessageRole
from domain.enums.audience_gender import AudienceGender
from domain.enums.decision_time import DecisionTime
from domain.enums.awareness_level import AwarenessLevel
from domain.enums.intensity_level import IntensityLevel
from domain.enums.purchasing_power import PurchasingPower
from domain.enums.fact_status import FactStatus

from infrastructure.ai.prompts.uniqueness import build_uniqueness_prompt



def generate_target_audience_handler(
    offer_profile_id: int
) -> Dict[str, Any]:
    container = Container()

    target_audience_repo = container.target_audiences_repository()
    
    ai_service = container.ai_service()
    offer_profile_service = container.offer_profile_service()
    offer_profile_context = offer_profile_service.build_llm_context(offer_profile_id=offer_profile_id)
    
    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt()
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=get_target_audience_prompt(offer_profile_context=offer_profile_context)
            )
        ]
    )

    response_json = json.loads(response.content )
    audiences_arr = response_json["audiences"]

    new_target_audiences = []
    for t in audiences_arr:
        new_target_audiences.append(
            TargetAudience(
                offer_profile_id=offer_profile_id,
                fact_status=FactStatus.UNVERIFIED.value,
                name=t["name"],
                reason=t["reason"],
                score=t['score'],
                confidence=t['confidence'],
                age_min=t["age_min"],
                age_max=t["age_max"],
                gender=t["gender"],
                location=t["location"],
                purchasing_power=t["purchasing_power"],
                lifestyles=t["lifestyles"],
                values=t["values"],
                awareness_level=t["awareness_level"],
                price_sensitivity=t["price_sensitivity"],
                research_level=t["research_level"],
                decision_time=t["decision_time"],
                pain_points=t["pain_points"],
                motivations=t["motivations"],
                buying_triggers=t["buying_triggers"],
                objections=t["objections"],
                message_angles=t["message_angles"],
                marketing_channels=t["marketing_channels"]
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

You analyze products and offers and transform product information
into practical customer insights.

Your goal is to determine:

1. Who is most likely to buy the product.
2. Why they will buy it.
3. How to effectively reach them.

Rules:
- Analyze the specific product.
- Do not create generic customer groups.
- Separate facts from assumptions.
- If data is missing, make realistic assumptions.
- Label assumptions.
- Results must be useful for advertising and marketing.

Requirements:
- confidence MUST be a float between 0 and 1.
- score MUST be an float between 0 and 1.

Return ONLY valid JSON.
"""


def get_target_audience_schema() -> str:
    return json.dumps(
{
    "audiences": [
        {
            "name": "",
            "score": 0,
            "confidence": 0,
            "reason": "",

            "age_min": 0,
            "age_max": 0,

            "gender": "",
            "location": "",
            "purchasing_power": "",

            "lifestyles": [""],
            "values": [""],

            "awareness_level": "",
            "price_sensitivity": "",
            "research_level": "",
            "decision_time": "",

            "pain_points": [""],
            "motivations": [""],
            "buying_triggers": [""],
            "objections": [""],

            "message_angles": [""],
            "marketing_channels": [""]
        }
    ]
}, ensure_ascii=False, indent=2)


def _enum_values(enum_cls) -> str:
    return ", ".join(member.value for member in enum_cls)


def get_enums_prompt() -> str:
    return f"""
Allowed enum values:

gender:
AudienceGenderEnum:
{_enum_values(AudienceGender)}

purchasing_power:
PurchasingPowerEnum:
{_enum_values(PurchasingPower)}

awareness_level:
AwarenessLevelEnum:
{_enum_values(AwarenessLevel)}

price_sensitivity:
IntensityLevelEnum:
{_enum_values(IntensityLevel)}

research_level:
IntensityLevelEnum:
{_enum_values(IntensityLevel)}

decision_time:
DecisionTimeEnum:
{_enum_values(DecisionTime)}


Enum rules:

- Enum fields must contain a single string value.
- Do not return arrays.
- Do not create new values.
- Use only values available in the corresponding enum.

Correct example:

"gender": "all"

Incorrect example:

"gender": ["male", "female"]
"""


def get_target_audience_prompt(offer_profile_context: str) -> str:
    return f"""
Analyze the product information.

PRODUCT DATA:

{offer_profile_context}


Generate target audience segments.


Response format:

{get_target_audience_schema()}


ENUM RULES:

{get_enums_prompt()}


Requirements:
- Return a minimum of 3 target audience segments.
- Do not invent random customers.
- Provide realistic segments.
- Include assumptions.
- JSON ONLY.
"""
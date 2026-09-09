import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.brand_marketing.brand_marketing import BrandMarketing


def generate_brand_marketing_handler(
    offer_profile_id: int
):
    container = Container()

    offer_profile_service = container.offer_profile_service()
    ai_service = container.ai_service()
    brand_marketing_repository = container.brand_marketing_repository()
    brand_marketing_service = container.brand_marketing_service()
    offer_profile_context = offer_profile_service.build_llm_context(offer_profile_id=offer_profile_id)

    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt()
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=get_data_prompt(offer_profile_context=offer_profile_context)
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content="Generate brand marketing strategy based on the provided data. Return only valid JSON using the specified structure."
            ),
        ]
    )

    content = response.content.strip()

    if content.startswith("```"):
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    data = json.loads(content)

    entity = BrandMarketing(
        offer_profile_id=offer_profile_id,
        brand_name=data.get("brand_name"),
        brand_positioning=data.get("brand_positioning"),
        brand_category=data.get("brand_category"),
        brand_target_customer=data.get("brand_target_customer"),
        brand_competitive_difference=data.get("brand_competitive_difference"),
        brand_purpose=data.get("brand_purpose"),
        brand_promise=data.get("brand_promise"),
        brand_personality=data.get("brand_personality", []),
        brand_values=data.get("brand_values", []),
        brand_voice=data.get("brand_voice"),
        brand_tone=data.get("brand_tone"),
        brand_tone_social_media=data.get("brand_tone_social_media"),
        brand_tone_customer_communication=data.get("brand_tone_customer_communication"),
        tagline=data.get("tagline"),
        unique_selling_proposition=data.get("unique_selling_proposition"),
        key_messages=data.get("key_messages", []),
        target_perception=data.get("target_perception", []),
        target_emotions=data.get("target_emotions", []),
        brand_associations=data.get("brand_associations", []),
        customer_desires=data.get("customer_desires", []),
        customer_pains=data.get("customer_pains", []),
        customer_fears=data.get("customer_fears", []),
        customer_objections=data.get("customer_objections", []),
        purchase_motivators=data.get("purchase_motivators", []),
        brand_story=data.get("brand_story"),
        brand_story_angle=data.get("brand_story_angle"),
        customer_transformation=data.get("customer_transformation"),
        content_pillars=data.get("content_pillars", []),
        storytelling_angles=data.get("storytelling_angles", []),
        ugc_direction=data.get("ugc_direction", []),
        visual_style=data.get("visual_style"),
        visual_direction=data.get("visual_direction"),
        brand_always_do=data.get("brand_always_do", []),
        brand_never_do=data.get("brand_never_do", []),
    )
    created = brand_marketing_repository.create(entity)

    return brand_marketing_service.get_brand_marketing_by_id(id=created.id)



def get_system_prompt() -> str:
    return """
You are an expert in brand strategy and brand marketing.

Your task is to analyze offer_profile base data:
- offer information,
- target audiences,
- customer voice,
- customer problems,
- objections,
- customer needs,
- customer values,
- market analysis.

Based on this information, create the foundation of the brand strategy.

Your goal is to define:
- how the brand should be positioned,
- how customers should perceive the brand,
- what makes the brand different,
- what emotions the brand should create,
- how the brand should communicate,
- what principles should guide future marketing activities.


Do not create:
- advertisements,
- sales campaigns,
- CTAs,
- advertising creatives,
- landing page copy,
- promotional slogans.

You create strategic brand foundations that will be used later by marketing, content, and creative generation systems.


RULES:

- Every decision must be based on the provided input data.
- If information is missing, create a reasonable strategic assumption.
- Clearly separate assumptions from confirmed information.
- Do not create fictional company history if it is not supported by the data.
- Focus on strategic direction, not advertising execution.


Your response must include:
- brand positioning,
- competitive differentiation,
- brand personality,
- brand values,
- communication style,
- emotional direction,
- customer perception,
- customer psychology,
- brand story direction,
- content direction,
- communication principles.


Return only valid JSON using exactly this structure:

{
    "brand_name": "",

    "brand_positioning": "",
    "brand_category": "",
    "brand_target_customer": "",
    "brand_competitive_difference": "",

    "brand_purpose": "",
    "brand_promise": "",

    "brand_personality": [],

    "brand_values": [],

    "brand_voice": "",

    "brand_tone": "",

    "brand_tone_social_media": "",

    "brand_tone_customer_communication": "",

    "tagline": "",

    "unique_selling_proposition": "",

    "key_messages": [],

    "target_perception": [],

    "target_emotions": [],

    "brand_associations": [],

    "customer_desires": [],

    "customer_pains": [],

    "customer_fears": [],

    "customer_objections": [],

    "purchase_motivators": [],

    "brand_story": "",

    "brand_story_angle": "",

    "customer_transformation": "",

    "content_pillars": [],

    "storytelling_angles": [],

    "ugc_direction": [],

    "visual_style": "",

    "visual_direction": "",

    "brand_always_do": [],

    "brand_never_do": []
}


STRICT JSON RULES:

- Return only valid JSON.
- Do not use markdown.
- Do not add explanations.
- Do not add text before JSON.
- Do not add text after JSON.
- Keep all JSON keys unchanged.
- Do not use null values.
- Do not omit required fields.
- Arrays must always be arrays.
- Objects must follow the required structure.
"""



def get_data_prompt(offer_profile_context: str) -> str:
    return f"""
OFFER_PROFILE:

{offer_profile_context}
"""

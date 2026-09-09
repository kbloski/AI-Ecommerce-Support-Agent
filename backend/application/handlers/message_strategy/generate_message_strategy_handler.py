import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.message_strategy.message_strategy import MessageStrategy



def generate_message_strategy_handler(
    offer_strategy_id: int
):

    container = Container()

    offer_profile_service = container.offer_profile_service()
    brand_marketing_service = container.brand_marketing_service()
    marketing_strategy_service = container.marketing_strategy_service()
    offer_strategy_service = container.offer_strategy_service()
    message_strategy_repository = container.message_strategy_repository()
    message_strategy_service = container.message_strategy_service()

    ai_service = container.ai_service()


    offer_strategy = offer_strategy_service.get_offer_strategy_by_id(
        id=offer_strategy_id
    )

    marketing_strategy = marketing_strategy_service.get_marketing_strategy_by_id(
        id=offer_strategy.marketing_strategy_id
    )

    brand_strategy = brand_marketing_service.get_brand_marketing_by_id(
        id=marketing_strategy.brand_marketing_id
    )

    offer_profile_context = offer_profile_service.build_llm_context(
        offer_profile_id=brand_strategy.offer_profile_id
    )

    brand_strategy_context = brand_marketing_service.build_llm_context(
        brand_marketing_id=marketing_strategy.brand_marketing_id
    )

    marketing_strategy_context = marketing_strategy_service.build_llm_context(
        marketing_strategy_id=offer_strategy.marketing_strategy_id
    )

    offer_strategy_context = offer_strategy_service.build_llm_context(
        offer_strategy_id=offer_strategy_id
    )



    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt()
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=get_data_prompt(
                    offer_profile_context=offer_profile_context,
                    brand_strategy_context=brand_strategy_context,
                    marketing_strategy_context=marketing_strategy_context,
                    offer_strategy_context=offer_strategy_context
                )
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content="Generate Message Strategy based on the provided data. Return only valid JSON using the specified structure."
            )
        ]
    )


    data = json.loads(response.content.strip())
    data = data.get("message_strategy", {})

    entity = MessageStrategy(
        offer_strategy_id=offer_strategy_id,
        core_message=data.get("core_message"),
        brand_message=data.get("brand_message"),
        primary_message_angle=data.get("primary_message_angle"),
        secondary_message_angles=data.get("secondary_message_angles", []),
        audience_messages=data.get("audience_messages", []),
        customer_pain_points=data.get("customer_pain_points", []),
        customer_desires=data.get("customer_desires", []),
        benefit_messages=data.get("benefit_messages", []),
        feature_to_benefit_mapping=data.get("feature_to_benefit_mapping", []),
        objection_handling_messages=data.get("objection_handling_messages", []),
        trust_messages=data.get("trust_messages", []),
        proof_points=data.get("proof_points", []),
        emotional_triggers=data.get("emotional_triggers", []),
        rational_arguments=data.get("rational_arguments", []),
        advertising_angles=data.get("advertising_angles", []),
        content_angles=data.get("content_angles", []),
        ugc_angles=data.get("ugc_angles", []),
    )
    created = message_strategy_repository.create(entity)

    return message_strategy_service.get_message_strategy_by_id(id=created.id)


def get_system_prompt() -> str:
    return """
You are an expert in Message Strategy
and marketing communication strategy.

Your task is to create a strategic communication framework
based on the available product, brand, customer,
and marketing context.


OBJECTIVE:

Define:
- what messages the brand should communicate,
- what customer problems should be addressed,
- what emotions should be activated,
- what rational arguments should be used,
- how customer objections should be handled.


Message Strategy is the foundation for future marketing assets generation.

It defines WHAT should be communicated, not HOW it should be written.

Message Strategy IS NOT:

- advertisements,
- headlines,
- slogans,
- landing page copy,
- email copy,
- social media posts.


Do not generate final marketing copy.



ANALYZE:


1. CORE MESSAGE

Define:

- the main idea customers should understand,
- the central value of the product,
- the main belief that should be created in the customer's mind.



2. BRAND MESSAGE

Define:

- how the brand should communicate,
- what the brand should stand for,
- what perception should be created.



3. MESSAGE ANGLES

Define:

- primary message angle,
- secondary message angles,
- different ways to communicate product value.


Each angle should explain:

- what it focuses on,
- why it matters to customers,
- when it should be used.



4. CUSTOMER PROBLEMS AND DESIRES

Define:

- customer pain points,
- customer frustrations,
- desired outcomes,
- emotional motivations,
- purchase motivations.



5. BENEFIT COMMUNICATION

Translate product value into communication:

Feature → Functional Benefit → Emotional Benefit → Customer Message


Example:

Feature:
"Water-resistant material"

Functional Benefit:
"Protects belongings from rain"

Emotional Benefit:
"Customer feels prepared and confident"

Message Direction:
"Stay protected in unpredictable situations"



6. OBJECTION HANDLING

Define:

- main customer objections,
- reasons behind objections,
- communication approach to overcome them.



7. TRUST AND PROOF COMMUNICATION

Define:

- trust-building messages,
- proof points,
- credibility factors,
- reasons customers should believe the product works.



8. ADVERTISING AND CONTENT DIRECTIONS

Define:

- advertising angles,
- content angles,
- UGC communication angles.

These are strategic directions,
not final creative concepts.



OUTPUT JSON:

{
    "message_strategy": {
        "core_message": "",
        "brand_message": "",
        "primary_message_angle": "",
        "secondary_message_angles": [
            {
                "angle": "",
                "focus": "",
                "customer_reason": ""
            }
        ],
        "audience_messages": [],
        "customer_pain_points": [],
        "customer_desires": [],
        "benefit_messages": [],
        "feature_to_benefit_mapping": [
            {
                "feature": "",
                "functional_benefit": "",
                "emotional_benefit": "",
                "communication_direction": ""
            }
        ],
        "objection_handling_messages": [
            {
                "objection": "",
                "customer_concern": "",
                "message_response": ""
            }
        ],
        "trust_messages": [],
        "proof_points": [],
        "emotional_triggers": [],
        "rational_arguments": [],
        "advertising_angles": [],
        "content_angles": [],
        "ugc_angles": []
    }
}



STRICT JSON RULES:
- Return only valid JSON.
"""



def get_data_prompt(
    offer_profile_context: str,
    brand_strategy_context: str,
    marketing_strategy_context: str,
    offer_strategy_context: str
) -> str:
    return f"""
OFFER_PROFILE BASE:

{offer_profile_context}



BRAND STRATEGY:

{brand_strategy_context}


MARKETING STRATEGY:

{marketing_strategy_context}


OFFER STRATEGY:

{offer_strategy_context}
"""
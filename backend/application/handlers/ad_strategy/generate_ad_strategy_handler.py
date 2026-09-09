import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.ad_strategy.ad_strategy import AdStrategy



def generate_ad_strategy_handler(
    message_strategy_id: int
):

    container = Container()


    offer_profile_service = container.offer_profile_service()

    brand_marketing_service = (
        container.brand_marketing_service()
    )

    marketing_strategy_service = (
        container.marketing_strategy_service()
    )

    offer_strategy_service = (
        container.offer_strategy_service()
    )

    message_strategy_service = (
        container.message_strategy_service()
    )

    ad_strategy_repository = container.ad_strategy_repository()
    ad_strategy_service = container.ad_strategy_service()

    ai_service = container.ai_service()



    message_strategy = (
        message_strategy_service.get_message_strategy_by_id(
            id=message_strategy_id
        )
    )

    offer_strategy = (
        offer_strategy_service.get_offer_strategy_by_id(
            id=message_strategy.offer_strategy_id
        )
    )

    marketing_strategy = (
        marketing_strategy_service.get_marketing_strategy_by_id(
            id=offer_strategy.marketing_strategy_id
        )
    )

    brand_strategy = (
        brand_marketing_service.get_brand_marketing_by_id(
            id=marketing_strategy.brand_marketing_id
        )
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
        offer_strategy_id=message_strategy.offer_strategy_id
    )

    message_strategy_context = message_strategy_service.build_llm_context(
        message_strategy_id=message_strategy_id
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
                    offer_strategy_context=offer_strategy_context,
                    message_strategy_context=message_strategy_context
                )
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content="Generate Ad Strategy based on the provided data. Return only valid JSON using the specified structure."
            )
        ]
    )



    try:

        content = response.content.strip()


        if content.startswith("```"):

            content = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )


        result = json.loads(content)


    except json.JSONDecodeError:

        result = {
            "raw_response": response.content
        }


    entity = AdStrategy(
        message_strategy_id=message_strategy_id,
        objective=result.get("objective"),
        customer_stage=result.get("customer_stage"),
        priority_audiences=result.get("priority_audiences", []),
        audience_angles=result.get("audience_angles", []),
        message_angles=result.get("message_angles", []),
        offer_angles=result.get("offer_angles", []),
        creative_concepts=result.get("creative_concepts", []),
        recommended_formats=result.get("recommended_formats", []),
        testing_hypotheses=result.get("testing_hypotheses", []),
    )
    created = ad_strategy_repository.create(entity)

    return ad_strategy_service.get_ad_strategy_by_id(id=created.id)




def get_system_prompt() -> str:
    return """
You are an expert in Advertising Strategy,
Performance Marketing, and Direct Response Marketing.


Your task is to create an AD STRATEGY
based on the complete marketing context.


Your goal is to answer:

"What advertisement should we create, for whom, with which argument, in what format, and why should it work?"


AD STRATEGY defines the strategic foundation of advertising.

It does NOT create:
- final copy,
- headlines,
- video scripts,
- finished advertisements,
- graphics,
- visual prompts.


GENERATE:


1. OBJECTIVE

Define:

- business goal,
- advertising goal,
- conversion event.



2. CUSTOMER STAGE

Define the current customer journey stage
and level of awareness.



3. PRIORITY AUDIENCES

Define:

- the most valuable audience segments,
- testing priority,
- why each segment is important.

Rules:

- Prioritize audiences with the highest purchase probability.
- Do not create generic demographic groups.
- Focus on customer motivations, problems, and buying situations.



4. AUDIENCE ANGLES

For each audience segment define:

- main pain point,
- customer desire,
- buying trigger.



5. MESSAGE ANGLES

Define strategic communication directions.

For each angle define:

- main argument,
- customer problem,
- strategic promise,
- customer objection,
- required proof.

Important:

- Define strategic messaging.
- Do not write advertising copy.



6. OFFER ANGLES

Define:

- how the product value should be presented,
- value mechanism,
- risk reduction strategy.



7. CREATIVE CONCEPTS

Define strategic creative directions that can later be developed into advertisements.

Do not create:

- scenes,
- scripts,
- hooks,
- dialogues,
- final advertising messages.

Define:

- concept name,
- strategic idea,
- message foundation,
- why it should work,
- recommended creative type,
- emotional direction.



8. RECOMMENDED FORMATS

Define advertising formats worth testing.

Examples:

- ugc_testimonial,
- product_demo,
- comparison,
- founder_story,
- before_after,
- static_benefit_ad.



9. TESTING HYPOTHESES

Create experimental hypotheses.

Define:

- what should be tested,
- variable,
- control,
- variant,
- success metric,
- priority.



Return only valid JSON:


{
    "objective": {
        "business_goal": "",
        "advertising_goal": "",
        "conversion_event": ""
    },

    "customer_stage": "",


    "priority_audiences": [
        {
            "segment": "",
            "priority": 1,
            "reason": ""
        }
    ],


    "audience_angles": [
        {
            "segment": "",
            "pain_point": "",
            "desire": "",
            "buying_trigger": ""
        }
    ],


    "message_angles": [
        {
            "angle": "",
            "problem": "",
            "promise": "",
            "objection": "",
            "proof_needed": ""
        }
    ],


    "offer_angles": [
        {
            "angle": "",
            "value_mechanism": "",
            "risk_reduction": ""
        }
    ],


    "creative_concepts": [
        {
            "name": "",
            "idea": "",
            "based_on_angle": "",
            "why_it_should_work": "",
            "recommended_creative_type": "",
            "emotional_direction": ""
        }
    ],


    "recommended_formats": [
        {
            "format": "",
            "reason": ""
        }
    ],


    "testing_hypotheses": [
        {
            "hypothesis": "",
            "variable": "",
            "control": "",
            "variant": "",
            "metric": "",
            "priority": ""
        }
    ]
}



STRICT JSON RULES:
- Return only valid JSON.
"""



def get_data_prompt(
    offer_profile_context: str,
    brand_strategy_context: str,
    marketing_strategy_context: str,
    offer_strategy_context: str,
    message_strategy_context: str
) -> str:
    return f"""
OFFER_PROFILE:
{offer_profile_context}


BRAND STRATEGY:
{brand_strategy_context}


MARKETING STRATEGY:
{marketing_strategy_context}


OFFER STRATEGY:
{offer_strategy_context}


MESSAGE STRATEGY:
{message_strategy_context}
"""


import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.offer_strategy.offer_strategy import OfferStrategy



def generate_offer_strategy_handler(
    marketing_strategy_id: int
):

    container = Container()

    offer_profile_service = container.offer_profile_service()
    brand_marketing_service = container.brand_marketing_service()
    marketing_strategy_service = container.marketing_strategy_service()
    ai_service = container.ai_service()
    offer_strategy_repository = container.offer_strategy_repository()
    offer_strategy_service = container.offer_strategy_service()



    marketing_strategy = marketing_strategy_service.get_marketing_strategy_by_id(
        id=marketing_strategy_id
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
        marketing_strategy_id=marketing_strategy_id
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
                    marketing_strategy_context=marketing_strategy_context
                )
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content="Generate an Offer Strategy based on the provided data. Return only valid JSON using the specified structure."
            ),
        ]
    )


    data = json.loads(response.content.strip())
    data = data.get("offer_strategy", {})

    entity = OfferStrategy(
        marketing_strategy_id=marketing_strategy_id,
        offer_name=data.get("offer_name"),
        offer_positioning=data.get("offer_positioning"),
        core_value_proposition=data.get("core_value_proposition"),
        main_customer_problem=data.get("customer_problem", {}).get("main_problem"),
        solution_mechanism=data.get("solution_mechanism"),
        primary_benefit=data.get("primary_benefit"),
        secondary_benefits=data.get("secondary_benefits", []),
        functional_benefits=data.get("functional_benefits", []),
        emotional_benefits=data.get("emotional_benefits", []),
        offer_structure=data.get("offer_structure", {}),
        value_stack=data.get("value_stack", []),
        risk_reversal=data.get("risk_reversal", []),
        trust_elements=data.get("trust_elements", []),
        pricing_strategy=data.get("pricing_strategy"),
        urgency_strategy=data.get("urgency_strategy"),
        customer_objection_handling=data.get("customer_objection_handling", []),
        competitive_difference=data.get("competitive_difference"),
        conversion_levers=data.get("conversion_levers", []),
    )
    created = offer_strategy_repository.create(entity)

    return offer_strategy_service.get_offer_strategy_by_id(id=created.id)


def get_system_prompt() -> str:
    return """
You are an expert in creating Offer Strategy
for e-commerce products, direct response marketing,
and conversion optimization.

Your task is to design an offer strategy
based on the available marketing context,
product information, and customer insights.


OBJECTIVE:

Answer the question:

"How should this product be packaged into an offer
that maximizes perceived value and increases
the probability of purchase?"


Offer Strategy IS NOT:

- an advertisement,
- a landing page,
- copywriting,
- headlines,
- slogans,
- marketing campaigns.


Your role is to define:

- how the product should be presented as an offer,
- why customers should choose this offer,
- what value matters most to the customer,
- what purchase barriers should be removed,
- what elements can increase conversion.



ANALYZE:


1. PRODUCT VALUE

Define:

- the main product value,
- the main customer outcome,
- the customer transformation after purchase,
- the strongest purchase reason.



2. CUSTOMER PROBLEM

Define:

- the main customer problem,
- the cost of the current situation,
- customer frustrations,
- consequences of not solving the problem.



3. OFFER POSITIONING

Define:

- how the offer should be positioned,
- who finds this offer most valuable,
- why customers should choose this offer,
- how it differs from alternatives.



4. VALUE STACK

Design the offer value structure:

- core product,
- included elements,
- additional value components,
- elements that increase perceived value.


Do not invent bonuses, services,
guarantees, or features that are not supported
by the provided context.

If something is a strategic recommendation,
mark it as an assumption.



5. RISK REVERSAL

Define:

- what risks customers perceive before purchase,
- what elements can reduce purchase risk,
- what increases customer confidence.



6. CUSTOMER OBJECTIONS

Define:

- main purchase objections,
- why customers may hesitate,
- how the offer should address them.



7. PURCHASE TRIGGER

Define:

- what can motivate the customer to buy now,
- what situation creates purchase intent,
- what increases urgency.



8. COMPETITIVE DIFFERENCE

Define:

- why this offer is better than alternatives,
- what differentiates the product,
- the strongest competitive advantage.



OUTPUT JSON:
{
    "offer_strategy": {
        "offer_name": "",
        "offer_positioning": "",
        "core_value_proposition": "",
        "customer_problem": {
            "main_problem": "",
            "pain_points": [],
            "cost_of_inaction": ""
        },
        "solution_mechanism": "",
        "primary_benefit": "",
        "secondary_benefits": [],
        "functional_benefits": [],
        "emotional_benefits": [],
        "offer_structure": {
            "core_product": "",
            "included_elements": [],
            "bonuses": [],
            "guarantee": "",
            "support": ""
        },
        "value_stack": [],
        "risk_reversal": [],
        "trust_elements": [],
        "pricing_strategy": "",
        "urgency_strategy": "",
        "purchase_trigger": "",
        "customer_objection_handling": [
            {
                "objection": "",
                "reason": "",
                "solution": ""
            }
        ],
        "competitive_difference": "",
        "conversion_levers": []
    }
}



STRICT JSON RULES:
- Return only valid JSON.
"""


def get_data_prompt(
    offer_profile_context: str,
    brand_strategy_context: str,
    marketing_strategy_context: str
) -> str:
    return f"""
OFFER_PROFILE:

{offer_profile_context}


BRAND STRATEGY:

{brand_strategy_context}


MARKETING STRATEGY:

{marketing_strategy_context}
"""
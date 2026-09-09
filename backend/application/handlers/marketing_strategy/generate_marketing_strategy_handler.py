import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.marketing_strategy.marketing_strategy import MarketingStrategy



def generate_marketing_strategy_handler(
    offer_profile_id: int,
    brand_markeging_id: int
):
    container = Container()

    offer_profile_service = container.offer_profile_service()
    brand_marketing_service = container.brand_marketing_service()
    brand_marketing_repository = container.brand_marketing_repository()
    ai_service = container.ai_service()
    marketing_strategy_repository = container.marketing_strategy_repository()
    marketing_strategy_service = container.marketing_strategy_service()

    brand_marketing = brand_marketing_repository.get_by_id(brand_markeging_id)
    if brand_marketing is None:
        raise ValueError(f"Brand marketing {brand_markeging_id} not found")
    if brand_marketing.offer_profile_id != offer_profile_id:
        raise ValueError(
            f"Brand marketing {brand_markeging_id} does not belong to offer_profile {offer_profile_id}"
        )

    offer_profile_context = offer_profile_service.build_llm_context(offer_profile_id=offer_profile_id)

    brand_strategy_context = brand_marketing_service.build_llm_context(
        brand_marketing_id=brand_markeging_id
    )


    user_prompt = get_data_prompt(
        offer_profile_context=offer_profile_context,
        brand_strategy_context=brand_strategy_context
    )


    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt()
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=user_prompt
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content="Generate marketing strategy based on the provided data. Return only valid JSON using the specified structure."
            )
        ]
    )


    data = json.loads(response.content.strip())

    entity = MarketingStrategy(
        brand_marketing_id=brand_markeging_id,
        marketing_objective=data.get("marketing_objective"),
        growth_strategy=data.get("growth_strategy"),
        primary_audience=data.get("primary_audience", []),
        secondary_audience=data.get("secondary_audience", []),
        audience_prioritization=data.get("audience_prioritization", []),
        customer_journey=data.get("customer_journey", {}),
        marketing_channels=data.get("marketing_channels", []),
        acquisition_strategy=data.get("acquisition_strategy", []),
        trust_building_strategy=data.get("trust_building_strategy", []),
        content_strategy=data.get("content_strategy", {}),
        community_strategy=data.get("community_strategy", []),
        creator_influencer_strategy=data.get("creator_influencer_strategy", []),
        campaign_directions=data.get("campaign_directions", []),
        conversion_strategy=data.get("conversion_strategy", []),
        retention_strategy=data.get("retention_strategy", []),
        marketing_experiments=data.get("marketing_experiments", []),
        marketing_kpis=data.get("marketing_kpis", []),
    )
    created = marketing_strategy_repository.create(entity)

    return marketing_strategy_service.get_marketing_strategy_by_id(id=created.id)




def get_system_prompt():
    return """
You are an expert in marketing strategy and growth marketing.

Your task is to create a marketing strategy based on the available context.

Your goal is to define:

- how to acquire customers,
- which channels to use,
- what the customer journey looks like,
- what marketing activities should be performed,
- how to build trust,
- which segments should be prioritized,
- which hypotheses should be tested.


Do not generate:
- advertisements,
- headlines,
- sales copy,
- landing pages,
- emails,
- creative assets.


Return only valid JSON:

{
    "marketing_objective": "",
    "growth_strategy": "",

    "primary_audience": [""],

    "secondary_audience": [""],

    "audience_prioritization": [
        {
            "audience": "",
            "reason": "",
            "potential": ""
        }
    ],

    "customer_journey": {
        "awareness": "",
        "consideration": "",
        "conversion": "",
        "retention": ""
    },

    "marketing_channels": [
        {
            "channel": "",
            "role": "",
            "strategy": ""
        }
    ],

    "acquisition_strategy": [""],

    "trust_building_strategy": [""],

    "content_strategy": {
        "main_pillars": [""],
        "content_goals": [""]
    },

    "community_strategy": [""],

    "creator_influencer_strategy": [""],

    "campaign_directions": [
        {
            "name": "",
            "objective": "",
            "audience": "",
            "strategic_angle": ""
        }
    ],

    "conversion_strategy": [""],

    "retention_strategy": [""],

    "marketing_experiments": [
        {
            "hypothesis": "",
            "area": "",
            "success_metric": ""
        }
    ],

    "marketing_kpis": [""]
}

Return valid JSON only.
"""


def get_data_prompt(offer_profile_context: str, brand_strategy_context: str) -> str:
    return f"""

OFFER_PROFILE BASE:

{offer_profile_context}

BRAND STRATEGY:

{brand_strategy_context}
"""
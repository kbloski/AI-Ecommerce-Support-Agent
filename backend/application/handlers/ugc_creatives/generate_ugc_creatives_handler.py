import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.ugc_creatives.ugc_creative import UgcCreative
from infrastructure.ai.prompts.uniqueness import build_uniqueness_prompt
from application.mappers.ugc_creative_mapper import UgcCreativeMapper


def generate_ugc_creatives_handler(
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

    ugc_creative_repository = container.ugc_creative_repository()
    ugc_creative_service = container.ugc_creative_service()

    ai_service = container.ai_service()

    ugc_creatives_db =  ugc_creative_repository.get_by_message_strategy_id(message_strategy_id=message_strategy_id)
    existed_ugc_creatives_str = json.dumps([UgcCreativeMapper.to_dto(i).to_dict() for i in ugc_creatives_db])

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



    response = ai_service.chat_llm(

        messages=[

            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt()
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=build_uniqueness_prompt(existed_ugc_creatives_str)
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=get_data_prompt(
                    offer_profile_context=offer_profile_service.build_llm_context(
                        offer_profile_id=brand_strategy.offer_profile_id
                    ),

                    brand_strategy_context=brand_marketing_service.build_llm_context(
                        brand_marketing_id=marketing_strategy.brand_marketing_id
                    ),

                    marketing_strategy_context=marketing_strategy_service.build_llm_context(
                        marketing_strategy_id=offer_strategy.marketing_strategy_id
                    ),

                    offer_strategy_context=offer_strategy_service.build_llm_context(
                        offer_strategy_id=message_strategy.offer_strategy_id
                    ),

                    message_strategy_context=message_strategy_service.build_llm_context(
                        message_strategy_id=message_strategy_id
                    )

                )
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content="Generate UGC Creatives based on the provided data. Return only valid JSON using the specified structure."
            ),
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

        return {
            "raw_response": response.content
        }


    created_ids = []


    for item in result.get("ugc_creatives", []):

        entity = UgcCreative(
            message_strategy_id=message_strategy_id,
            name=item.get("name"),
            customer_persona=item.get("customer_persona"),
            content_format=item.get("content_format"),
            angle=item.get("angle"),
            hook_idea=item.get("hook_idea"),
            video_flow=item.get("video_flow", []),
            recording_style=item.get("recording_style"),
            platform_fit=item.get("platform_fit", []),
            cta=item.get("cta"),
            why_it_should_work=item.get("why_it_should_work"),
        )

        created = ugc_creative_repository.create(entity)

        created_ids.append(created.id)


    return [
        ugc_creative_service.get_ugc_creative_by_id(id)
        for id in created_ids
    ]



def get_system_prompt() -> str:
    return """
You are an expert in:

- Organic UGC Content
- Customer Generated Content
- E-commerce Marketing
- Direct Response Marketing
- Performance Creative
- Consumer Psychology
- Product Demonstration Content

Your task is to create proposals for NATURAL UGC MATERIALS
for an e-commerce product.

The materials should look like content recorded by real customers
using their phones, not professional advertisements created by a brand.



GOAL:

Create content ideas that look like:

- a regular customer post,
- a phone-recorded video,
- a spontaneous recommendation,
- showing the product in everyday use,
- a reaction after purchase,
- solving a real customer problem.



DO NOT GENERATE:

- professional advertisements,
- advertising slogans,
- acting scripts,
- sales dialogues,
- TV commercials,
- productions requiring a professional film crew,
- graphics,
- visual prompts.



1. CUSTOMER PERSONA

Define the person recording the content:

- customer type,
- life situation,
- problem they had before purchasing,
- why they naturally use the product.



2. CONTENT FORMAT

Define the video format.

Examples:

- selfie review,
- first impression,
- unboxing,
- product test,
- before/after,
- "I bought this because...",
- problem → solution,
- daily routine,
- comparison with old solution,
- unexpected discovery.



3. CONTENT ANGLE

Define the main topic of the content.

Examples:

- saving time,
- solving frustration,
- first results after using the product,
- convenience,
- simplicity of use,
- discovering a new solution.



4. HOOK IDEA

Create an idea for the first seconds of the video.

It should feel natural,
like the beginning of a video uploaded by a real customer.

Do not create advertising hooks such as:

"You won't believe..."
"This product will change everything..."



5. VIDEO FLOW

Define the general flow of the recording.

Do not create a full script.

Return only the stages:

[
    "showing the problem",
    "showing the product",
    "first use",
    "showing the result",
    "user opinion"
]



6. RECORDING STYLE

Define how the content should look.

Examples:

- handheld phone recording,
- natural lighting,
- home environment,
- no professional editing,
- spontaneous narration.



7. PLATFORM FIT

Define where the content fits.

Examples:

- TikTok,
- Instagram Reels,
- Facebook Ads,
- Meta Feed,
- Stories.



8. CTA

Create a natural call to action.

Do not use aggressive selling.

Examples:

- "Check it yourself",
- "Learn more",
- "Link in bio".



9. WHY IT SHOULD WORK

Explain:

- what psychological mechanism works,
- why customers will believe this content,
- what customer objections it removes.



OUTPUT JSON:

{
    "ugc_creatives":[
        {
            "name":"",
            "customer_persona":
                {
                    "type":"",
                    "situation":"",
                    "problem":"",
                    "why_this_person_works":""
                },
            "content_format":"",
            "angle":"",
            "hook_idea":"",
            "video_flow":[],
            "recording_style":"",
            "platform_fit":[],
            "cta":"",
            "why_it_should_work":""
        }
    ]
}


RULES:
- Return only JSON.
- Materials must look like recordings created by real customers,
  not advertisements created by the brand.
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
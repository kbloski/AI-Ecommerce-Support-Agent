import json

from di.container import Container
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.llm.llm_message import LlmMessage
from application.mappers.offer_profile_mapper import OfferProfileMapper
from domain.models.checklist.checklist_item import ChecklistItem
from application.mappers.checklist_item_mapper import ChecklistItemMapper


SYSTEM_PROMPT = """
You are an expert in e-commerce product research and dropshipping validation.

Your task is to create detailed TODO checklists that help verify the market potential of a product before starting sales.

You do not directly judge or rate the product. Instead, you create research instructions that a user can execute step by step.

Every generated task must:
- be a specific action to perform,
- contain detailed instructions on how to complete the analysis,
- specify where the research should be performed,
- include example search phrases/queries,
- describe what data should be collected,
- explain how to interpret the results.

You work using these research methods:
- Google Trends research,
- Meta Ads Library research,
- TikTok Creative Center research,
- marketplace research (Amazon, AliExpress, Temu, eBay),
- customer review analysis,
- social media research.

Important requirements:

For every task that requires searching, keyword research, ads research, marketplace research, or social media research:

- provide a minimum of 10-15 concrete search phrases,
- provide realistic keywords based on the analyzed product,
- provide hashtags when applicable,
- provide copy-paste ready search queries,
- do not use placeholders.

Do not write:
- "keyword1"
- "keyword2"
- "product name"

Generate real search examples based on the product information.

Every task must be possible to complete without additional offer_profile.

Do not create generic advice.

Do not write:
"check competitors"

Instead, provide exact instructions:
- where to go,
- what to search for,
- what to analyze,
- what data to collect,
- what indicates a positive or negative signal.

The response MUST be ONLY a valid JSON array.

Each element must have exactly this structure:

[
  {
    "title": "task name",
    "description": "detailed task execution instructions",
    "note": "additional information or empty string"
  }
]

Do not add any text outside the JSON.

Values must be in polish.



The research must be prepared specifically for the Polish market.

The generated content can use Polish or English keywords depending on how customers actually search in Poland.

Do not translate keywords artificially.
If an English keyword is commonly used in Poland (for example product names, trends, TikTok phrases, brand-related searches), keep the English version.

Adapt all research to:
- Polish customers,
- Polish e-commerce market,
- Polish competitors,
- Polish shopping behavior,
- Polish marketplaces,
- Polish social media trends.

Search phrases should reflect real queries used by people in Poland, not only direct translations from English.
"""


def prepare_user_prompt(json_offer_data: str) -> str:
    return f"""
Based on the product data, prepare a product research checklist.

Product data:

{json_offer_data}


Generate a list of tasks that the user should perform to validate the potential of this product.


Important:

Every task involving search must contain:
- minimum 10-15 search phrases,
- specific keywords,
- relevant variations,
- ready-to-use queries,
- instructions how to use them.

The user should be able to copy and paste your generated phrases directly into research tools.


Include:


1. Google Trends:

Create tasks related to:

- analyzing the main product keywords,
- analyzing customer problems,
- analyzing alternative product names,
- analyzing seasonality,
- analyzing related searches.

For every Google Trends task provide:

- minimum 10-15 search phrases,
- product keywords,
- problem-based keywords,
- alternative names,
- related terms,
- instructions where to search,
- instructions what to check,
- instructions how to interpret results.


2. Meta Ads Library:

Create tasks related to:

- searching for product advertisements,
- searching for competitor advertisements,
- searching based on customer problems,
- analyzing successful running ads.

For every Meta Ads Library task provide:

- minimum 15 search queries,
- product name variations,
- customer problem phrases,
- desired outcome phrases,
- emotional buying triggers.

Explain:

- how to filter results,
- what ads to analyze,
- what elements to collect:
  - hook,
  - creative,
  - offer,
  - comments,
  - engagement,
  - advertising duration.


3. TikTok Creative Center:

Create tasks related to:

- analyzing product popularity,
- analyzing hashtags,
- analyzing viral videos,
- analyzing user comments.

For every TikTok task provide:

- minimum 15 hashtags,
- minimum 10 search phrases,
- content angles to investigate.

Explain:

- where to search,
- what metrics to analyze,
- what comments indicate buying intent.


4. Marketplace research:

Create separate tasks for:

- Amazon,
- AliExpress,
- Temu,
- eBay.

For every marketplace provide:

- minimum 10 search phrases,
- product variations,
- alternative names,
- related categories.

Analyze:

- number of reviews,
- product rating,
- sales indicators,
- customer complaints,
- repeated problems,
- customer expectations.


5. Customer review analysis:

Create tasks related to:

- finding negative reviews,
- finding purchase motivations,
- finding common problems,
- finding product improvement opportunities.

Explain:

- where to search,
- what phrases to look for,
- what information to extract,
- how to use findings to improve the offer.


6. Social media research:

Create tasks for:

- TikTok,
- Instagram,
- YouTube,
- Pinterest.

For every platform provide:

- minimum 10 search phrases,
- minimum 15 hashtags when applicable,
- content examples to analyze.

Explain:

- what videos to review,
- what comments matter,
- what signals indicate real interest.


7. Final product audit:

Add a final summary task.

It should explain:

- how to collect all research results,
- how to compare findings,
- what criteria evaluate product potential,
- how to decide whether the product moves to the next stage.


Every task must be a practical execution instruction.

Bad example:

"Check competitors"


Good example:

"Analyze competitor ads in Meta Ads Library:

1. Open Meta Ads Library.
2. Search using:
- portable blender
- mini smoothie maker
- travel blender
- USB blender
- fitness blender bottle

3. Save active advertisements.
4. Analyze:
- hooks,
- offers,
- creatives,
- comments,
- how long ads have been running."


Return ONLY a JSON array following the format defined in the SYSTEM PROMPT.
"""


def analyse_checklist_generate_handler(
    offer_profile_id: int,
    analyse_id: int,
    checklist_id: int
):
    container = Container()

    logger = container.logger()
    ai_service = container.ai_service()
    offer_profile_service = container.offer_profile_service()
    checklist_items_repository = container.checklist_items_repository()

    logger.info(
        f"Checklist generation started. "
        f"offer_profile_id={offer_profile_id}, analyse_id={analyse_id}, checklist_id={checklist_id}"
    )

    # ---------
    # Get product data
    # ---------

    logger.info("Fetching product offer_profile data")



    logger.info("Assembling product offer_profile")

    assembled_offer_profile = offer_profile_service.get_offer_profile_details_by_id(offer_profile_id=offer_profile_id)


    json_offer_data = json.dumps(
        assembled_offer_profile.to_dict(),
        ensure_ascii=False,
        indent=2
    )

    logger.info(
        f"Product data prepared. Size={len(json_offer_data)} chars"
    )


    # ---------
    # Prepare prompt
    # ---------

    logger.info("Preparing user prompt")

    user_prompt = prepare_user_prompt(
        json_offer_data=json_offer_data
    )

    logger.info(
        f"User prompt prepared. Size={len(user_prompt)} chars"
    )


    # ---------
    # Call LLM
    # ---------

    logger.info("Sending request to LLM")

    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=SYSTEM_PROMPT
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=user_prompt
            )
        ]
    )

    logger.info("LLM response received")


    # ---------
    # Checklist Items Create
    # ---------

    logger.info("Parsing LLM response")

    response_object = json.loads(
        response.content
    )

    logger.info(
        f"Generated checklist items count={len(response_object)}"
    )


    checklist_items = []

    for index, item in enumerate(response_object):

        logger.info(
            f"Creating checklist item {index + 1}: {item['title']}"
        )

        checklist_items.append(
            ChecklistItem(
                checklist_id=checklist_id,
                title=item["title"],
                description=item["description"],
                note=item.get("note", "")
            )
        )


    logger.info(
        f"Saving checklist items. Count={len(checklist_items)}"
    )

    checklist_items_db = checklist_items_repository.create_many(
        items=checklist_items
    )


    logger.info(
        f"Checklist items saved. Count={len(checklist_items_db)}"
    )


    items_dtos = [
        ChecklistItemMapper.to_dto(ch)
        for ch in checklist_items_db
    ]

    logger.info("Checklist generation finished")

    return items_dtos
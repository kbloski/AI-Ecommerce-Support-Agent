# ----------------------------
# Prepare dto result
# ----------------------------
import json

from application.mappers.offer_profile_mapper import OfferProfileMapper
from application.dtos.offers.offer_dto import OfferDto

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole

from domain.models.offer_profiles.offer_profile import OfferProfile


from infrastructure.database.db import SessionLocal



# =====================================================`r`n# MAIN HANDLER
# =====================================================

def offer_profile_generate_handler(offer_id: int):

    container = Container()

    offer_service = container.offer_service()
    ai_service = container.ai_service()


    # ----------------------------
    # LOAD OFFER
    # ----------------------------
    offer_context = offer_service.build_llm_context(offer_id)


    # ----------------------------
    # GENERATE OFFER_PROFILE
    # ----------------------------

    chat = [
        LlmMessage(
            role=LlmMessageRole.SYSTEM,
            content=get_system_prompt()
        ),
        LlmMessage(
            role=LlmMessageRole.USER,
            content=get_data_prompt(offer_context)
        ),
        LlmMessage(
            role=LlmMessageRole.USER,
            content=get_offer_profile_prompt()
        ),
    ]

    response = ai_service.chat_llm(chat).content

    json_data = json.loads(response)

    # ----------------------------
    # SAVE TO DATABASE
    # ----------------------------
    with SessionLocal() as session:
        with session.begin():

            offer_profile = OfferProfile(
                offer_id=offer_id,
                offer_summary=json_data.get("offer_summary", ""),
                category=json_data.get("category", ""),
                value_proposition=json_data.get("value_proposition", ""),
            )

            session.add(offer_profile)
            session.flush()
            session.refresh(offer_profile)

            saved_insights = list(insight_items)


    # ----------------------------
    # PREPARE DTO RESULT
    # ----------------------------

    result = OfferProfileMapper.to_dto(
        offer_profile
    )
    return result



# =====================================================
# BASE ROLE
# =====================================================

def get_system_prompt() -> str:
    return """
You are a senior product strategist AI specialized in product analysis,
market research, customer psychology, and marketing strategy.

Your role is to deeply understand offers and transform raw offer
information into structured business offer_profile.

Think like:
- a product manager,
- a market researcher,
- a growth strategist.

Rules:
- Understand before analyzing.
- Be specific to the offer.
- Avoid generic statements.
- Separate facts from assumptions.
- Make reasonable assumptions when data is incomplete.
- Focus on business value.

Return ONLY valid JSON.
Do not use markdown.
"""



# =====================================================
# OFFER_PROFILE PROMPT
# =====================================================
def get_data_prompt( offer_context : str) -> str:
    return f"""
OFFER DATA:

{offer_context}
"""

# =====================================================
# OFFER_PROFILE PROMPT
# =====================================================
def get_offer_profile_prompt() -> str:
    return """
Analyze the offer information and create a deep understanding of this offer.

Your goal is to build a structured offer_profile base that explains:
what this offer is, why it exists, what value it provides, and what makes it different.

Analyze the offer from the perspective of a senior product strategist.

Understand:

- What this offer actually is
- What category or market it belongs to
- What customer problem, need, or situation it addresses
- What solution it provides
- What transformation or outcome it creates
- Who it is potentially designed for
- Main components and elements included in the offer
- Key features
- Functional benefits
- Emotional benefits
- Value proposition
- Differentiation factors
- Strengths of the offer
- Possible weaknesses or limitations
- Important observations about the offer

Rules:

- Focus on understanding the offer itself.
- Do not create detailed customer personas yet.
- Do not create marketing campaigns or sales copy yet.
- Do not generate advertising messages yet.
- Separate facts from assumptions.
- If information is incomplete, make reasonable assumptions and clearly mark them.
- Add additional fields if they provide meaningful value for understanding the offer.
- Avoid generic statements. Stay specific to this offer.

Additional insight extraction rules:

- Extract the maximum possible number of meaningful insights about the offer.
- Do not limit the number of insights in any section.
- Lists do not need to contain the same number of elements.
- Some sections may contain many insights, while others may contain only a few or none if no meaningful information exists.
- Prioritize discovering valuable information over maintaining balanced output.
- Do not artificially create items just to fill sections.
- Include every relevant insight that can be logically derived from the offer information.

Important:
    - Do not create detailed personas.
    - Do not create advertising messages.
    - Do not create marketing campaigns.
    - Focus only on understanding the offer.
    - If something is uncertain, mark it as assumption.

Return ONLY valid JSON.

Use this structure as a foundation, but extend it when necessary:

{
    "offer_summary": "",
    "category": "",
    "problem_solved": [],
    "solution": [],
    "transformation": [],
    "offer_components": [],
    "features": [],
    "functional_benefits": [],
    "emotional_benefits": [],
    "value_proposition": "",
    "differentiators": [],
    "strengths": [],
    "limitations": [],
    "additional_insights": []
}
"""







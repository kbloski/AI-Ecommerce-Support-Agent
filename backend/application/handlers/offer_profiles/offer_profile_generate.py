import json

from application.mappers.offer_profile_mapper import OfferProfileMapper
from application.services.llm_context_builder import build_llm_section

from di.container import Container

from domain.models.llm.llm_message import LlmMessage
from domain.models.offer_profiles.offer_profile import OfferProfile
from domain.models.offer_profiles.offer_profile_element import OfferProfileElement

from domain.enums.llm_message_role import LlmMessageRole
from domain.enums.offer_profile_element_type import (
    OfferProfileElementType,
    get_offer_profile_element_type_values,
)

from infrastructure.database.db import SessionLocal


# =====================================================
# MAIN HANDLER
# =====================================================

def offer_profile_generate_handler(offer_id: int):

    container = Container()

    offer_service = container.offer_service()
    ai_service = container.ai_service()

    # ----------------------------
    # LOAD OFFER
    # ----------------------------

    offer_context = offer_service.build_llm_context(
        offer_id=offer_id
    )

    # ----------------------------
    # GENERATE OFFER PROFILE
    # ----------------------------

    chat = [
        LlmMessage(
            role=LlmMessageRole.SYSTEM,
            content=get_system_prompt()
        ),
        LlmMessage(
            role=LlmMessageRole.USER,
            content=get_data_prompt(
                offer_context=offer_context
            )
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
                offer_summary=json_data.get(
                    "offer_summary",
                    ""
                ),
                category=json_data.get(
                    "category",
                    ""
                ),
                value_proposition=json_data.get(
                    "value_proposition",
                    ""
                ),
            )

            session.add(offer_profile)
            session.flush()

            for element_data in json_data.get("offer_elements", []):

                if not isinstance(element_data, dict):
                    continue

                try:
                    element_type = OfferProfileElementType(
                        element_data.get("type")
                    )
                except (TypeError, ValueError):
                    continue

                name = str(
                    element_data.get("name", "")
                ).strip()

                if not name:
                    continue

                description = (
                    str(
                        element_data.get(
                            "description",
                            ""
                        )
                    ).strip()
                    or None
                )

                session.add(
                    OfferProfileElement(
                        offer_profile_id=offer_profile.id,
                        type=element_type,
                        name=name,
                        description=description,
                    )
                )

            session.flush()
            session.refresh(offer_profile)

        # ----------------------------
        # PREPARE DTO RESULT
        # ----------------------------

        result = OfferProfileMapper.to_dto(
            offer_profile
        )

    return result


# =====================================================
# SYSTEM PROMPT
# =====================================================

def get_system_prompt() -> str:
    return """
You are a senior product strategist AI specialized in product analysis,
market research, customer psychology, and marketing strategy.

Your role is to deeply understand offers and transform raw offer
information into structured business offer profiles.

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
# OFFER DATA PROMPT
# =====================================================

def get_data_prompt(offer_context: str) -> str:
    return f"""
OFFER DATA:

{offer_context}
"""


# =====================================================
# OFFER PROFILE PROMPT
# =====================================================

def get_offer_profile_prompt() -> str:
    return f"""
Analyze the offer information and create a deep understanding of this offer.

Your goal is to build a structured offer profile that explains:
what this offer is, why it exists, what value it provides,
and what makes it different.

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
- If information is incomplete, make reasonable assumptions
  and clearly mark them.
- Avoid generic statements.
- Stay specific to this offer.


Additional insight extraction rules:

- Extract the maximum possible number of meaningful insights
  about the offer.
- Do not limit the number of insights in any section.
- Lists do not need to contain the same number of elements.
- Some sections may contain many insights, while others may
  contain only a few or none if no meaningful information exists.
- Prioritize discovering valuable information over maintaining
  balanced output.
- Do not artificially create items just to fill sections.
- Include every relevant insight that can be logically derived
  from the offer information.


OFFER ELEMENT TYPES:

{get_offer_element_types_prompt()}


OFFER ELEMENT GENERATION RULES:

- "offer_elements" represents structured knowledge about the offer.
- Each element belongs to one of the available OfferProfileElementType values.
- Element types represent different aspects of the offer, such as benefits,
  features, problems solved, use cases, differentiators, limitations,
  or other supported element categories.
- Analyze the offer separately for EACH available element type.
- Generate meaningful elements for every type for which relevant information
  can be extracted or reasonably derived from the offer.
- Do not generate only benefits.
- Do not prefer one element type simply because it appears in the schema example.
- The example type shown in the JSON schema is only an example of a valid enum value.
- Multiple elements may have the same type.
- Different element types may contain different numbers of elements.
- A type may have zero elements if the offer provides no meaningful information
  for that category.
- Do not create artificial elements merely to ensure every type is present.
- Prefer multiple specific elements over one broad generic element.
- "name" should be short and clearly identify the insight.
- "description" should explain what the element means specifically
  in the context of this offer.


Important:

- Do not create detailed personas.
- Do not create advertising messages.
- Do not create marketing campaigns.
- Focus only on understanding the offer.
- If something is uncertain, mark it as an assumption.


Each object inside "offer_elements" MUST match this schema:

{get_offer_elements_schema()}

"offer_elements" is an array and may contain zero or more objects.
Use only the allowed values for "type".


The complete response MUST match this schema:

{get_output_schema()}


Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside the JSON.
"""


# =====================================================
# OFFER ELEMENT TYPES PROMPT
# =====================================================

def get_offer_element_types_prompt() -> str:
    return build_llm_section(
        tag="offer_element_types",
        content=json.dumps(
            get_offer_profile_element_type_values(),
            ensure_ascii=False,
            indent=2
        )
    )


# =====================================================
# OFFER ELEMENT SCHEMA
# =====================================================

def get_offer_elements_schema() -> str:
    return build_llm_section(
        tag="offer_elements_schema",
        content=json.dumps(
            {
                "type": "",
                "name": "",
                "description": "",
            },
            ensure_ascii=False,
            indent=2
        )
    )


# =====================================================
# OUTPUT SCHEMA
# =====================================================

def get_output_schema() -> str:
    return build_llm_section(
        tag="output_schema",
        content=json.dumps(
            {
                "offer_summary": "",
                "category": "",
                "value_proposition": "",
                "offer_elements": [
                    {
                        "type": "",
                        "name": "",
                        "description": "",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2
        )
    )
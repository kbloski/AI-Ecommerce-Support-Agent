from di.container import Container
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.llm.llm_message import LlmMessage
from domain.models.page_blueprint.page_blueprint import PageBlueprint
from application.services.llm_result_validation import (
    LlmGenerationError,
    parse_llm_json,
    require_dict,
    require_list,
    validate_ordered_sections,
)

ALLOWED_SECTION_PRIORITIES = {"required", "optional"}


def generate_page_blueprint_handler(page_requirements_id: int):
    container = Container()
    logger = container.logger()

    logger.info(
        "generate_page_blueprint_handler: start "
        f"page_requirements_id={page_requirements_id}"
    )

    page_requirements_service = container.page_requirements_service()
    page_strategy_service = container.page_strategy_service()
    message_strategy_service = container.message_strategy_service()
    offer_profile_service = container.offer_profile_service()
    brand_marketing_service = container.brand_marketing_service()
    marketing_strategy_service = container.marketing_strategy_service()
    offer_strategy_service = container.offer_strategy_service()
    page_sections_service = container.page_sections_service()
    page_blueprint_repository = container.page_blueprint_repository()
    page_blueprint_service = container.page_blueprint_service()
    ai_service = container.ai_service()

    # -------------------------------------------------------------------------
    # Resolve pipeline context
    # -------------------------------------------------------------------------

    page_requirements = page_requirements_service.get_page_requirements_by_id(
        id=page_requirements_id
    )

    page_strategy = page_strategy_service.get_page_strategy_by_id(
        id=page_requirements.page_strategy_id
    )

    message_strategy = message_strategy_service.get_message_strategy_by_id(
        id=page_strategy.message_strategy_id
    )

    offer_strategy = offer_strategy_service.get_offer_strategy_by_id(
        id=message_strategy.offer_strategy_id
    )

    marketing_strategy = marketing_strategy_service.get_marketing_strategy_by_id(
        id=offer_strategy.marketing_strategy_id
    )

    brand_strategy = brand_marketing_service.get_brand_marketing_by_id(
        id=marketing_strategy.brand_marketing_id
    )

    logger.info(
        "generate_page_blueprint_handler: ancestor chain resolved "
        f"page_strategy_id={page_strategy.id} "
        f"message_strategy_id={message_strategy.id} "
        f"offer_strategy_id={offer_strategy.id} "
        f"marketing_strategy_id={marketing_strategy.id} "
        f"brand_marketing_id={brand_strategy.id} "
        f"section_requirements_count="
        f"{len(page_requirements.page_section_requirements)}"
    )

    # -------------------------------------------------------------------------
    # Build context
    # -------------------------------------------------------------------------

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
        message_strategy_id=page_strategy.message_strategy_id
    )

    page_strategy_context = page_strategy_service.build_llm_context(
        page_strategy_id=page_requirements.page_strategy_id
    )

    page_requirements_context = page_requirements_service.build_llm_context(
        page_requirements_id=page_requirements_id
    )

    page_section_types_context = (
        page_sections_service.build_llm_context_for_requirements(
            page_requirements_id=page_requirements_id
        )
    )

    # -------------------------------------------------------------------------
    # Build prompts
    # -------------------------------------------------------------------------

    system_prompt = get_system_prompt()

    user_prompt = get_data_prompt(
        offer_profile_context=offer_profile_context,
        brand_strategy_context=brand_strategy_context,
        marketing_strategy_context=marketing_strategy_context,
        offer_strategy_context=offer_strategy_context,
        message_strategy_context=message_strategy_context,
        page_strategy_context=page_strategy_context,
        page_requirements_context=page_requirements_context,
        page_section_types_context=page_section_types_context,
    )

    logger.info(
        "generate_page_blueprint_handler: sending request to LLM"
    )

    # -------------------------------------------------------------------------
    # Generate Page Blueprint
    # -------------------------------------------------------------------------

    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=system_prompt,
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=user_prompt,
            ),
        ]
    )

    logger.info(
        "generate_page_blueprint_handler: LLM response received "
        f"length={len(response.content or '')}"
    )

    # -------------------------------------------------------------------------
    # Parse and validate response structure before any write
    # -------------------------------------------------------------------------

    try:
        result = parse_llm_json(response.content)
        page_blueprint_data = require_dict(
            result.get("page_blueprint"), "page_blueprint", raw_response=response.content
        )
        sections = require_list(
            page_blueprint_data.get("sections"), "page_blueprint.sections", raw_response=response.content
        )
        allowed_section_types = page_sections_service.get_allowed_ids()
        validate_ordered_sections(
            sections,
            allowed_section_types=allowed_section_types,
            allowed_priorities=ALLOWED_SECTION_PRIORITIES,
            raw_response=response.content,
        )
    except LlmGenerationError as e:
        logger.error(f"generate_page_blueprint_handler: {e.message}")
        raise

    logger.info(
        "generate_page_blueprint_handler: "
        f"parsed {len(sections)} sections"
    )

    # -------------------------------------------------------------------------
    # Save Page Blueprint
    # -------------------------------------------------------------------------

    entity = PageBlueprint(
        page_strategy_id=page_strategy.id,
        page_requirements_id=page_requirements_id,
        page_type=page_blueprint_data.get(
            "page_type",
            "ecommerce_product",
        ),
        primary_conversion_goal=page_blueprint_data.get(
            "primary_conversion_goal",
            "purchase",
        ),
        sections=sections,
    )

    logger.info(
        "generate_page_blueprint_handler: creating PageBlueprint "
        f"page_strategy_id={entity.page_strategy_id} "
        f"page_requirements_id={entity.page_requirements_id} "
        f"page_type={entity.page_type} "
        f"primary_conversion_goal={entity.primary_conversion_goal} "
        f"sections_count={len(entity.sections or [])}"
    )

    try:
        created = page_blueprint_repository.create(entity)

    except Exception as e:
        logger.error(
            "generate_page_blueprint_handler: "
            f"failed to save PageBlueprint - {e}"
        )
        raise

    logger.info(
        "generate_page_blueprint_handler: "
        f"saved PageBlueprint id={created.id}"
    )

    saved = page_blueprint_service.get_page_blueprint_by_id(
        id=created.id
    )

    logger.info(
        "generate_page_blueprint_handler: done, "
        f"returning PageBlueprint id={created.id}"
    )

    return saved


def get_system_prompt() -> str:
    return """
You are an expert in:

- E-commerce Landing Page Architecture
- Conversion Rate Optimization
- Direct Response Marketing
- Product Page Psychology
- Customer Journey Design
- Consumer Psychology


YOUR TASK

Create a PAGE BLUEPRINT for a sales-focused landing page.

A Page Blueprint defines:

- which sections should exist,
- their final order,
- the strategic purpose of every section,
- the role of every section in the customer journey,
- the psychological goal of every section,
- the information required later to generate content,
- supported proof that may be used,
- real objections that should be addressed.

A Page Blueprint is NOT final copy.


DO NOT GENERATE

- headlines,
- subheadlines,
- body copy,
- CTA copy,
- sales copy,
- advertising copy,
- HTML,
- CSS,
- UI components,
- visual design,
- images.


PAGE REQUIREMENTS are explicit user constraints.

They always have the highest priority.


PAGE REQUIREMENTS

Each section may have one of these requirement types:


"required"

The section MUST appear in the blueprint.


"optional"

The section may appear when it has a clear strategic role.


"excluded"

The section MUST NOT appear in the blueprint.


If a section has a `position`, place that section
at that exact 1-based position.

Treat explicit positions as structural constraints.

Assume PAGE REQUIREMENTS are internally valid.


PAGE SECTION TYPES CONTEXT

PAGE SECTION TYPES CONTEXT is the authoritative source
for available section types.

Use it to understand:

- which `section_type` values exist,
- what each section type means,
- the intended purpose of each section type,
- any category or metadata associated with the section type.

Use ONLY section types present in PAGE SECTION TYPES CONTEXT.

Never:

- invent a new section_type,
- rename a section_type,
- modify a section_type identifier,
- combine section types into a new identifier,
- output a section type that is not present in the context.


SECTION SELECTION

Build the page structure in this order:


STEP 1 — REQUIRED SECTIONS

Include every section explicitly marked `required`
in PAGE REQUIREMENTS.

A required section may never be omitted.


STEP 2 — EXCLUDED SECTIONS

Never include a section marked `excluded`.

An excluded section may never appear in the blueprint,
even if it would normally be useful.


STEP 3 — OPTIONAL SECTIONS

Evaluate optional sections using:

- PAGE STRATEGY,
- PAGE SECTION TYPES CONTEXT,
- OFFER STRATEGY,
- MESSAGE STRATEGY,
- MARKETING STRATEGY,
- BRAND STRATEGY,
- OFFER_PROFILE.

Include an optional section only when it has a clear
strategic role on this specific page.

A section may be useful when it helps:

- communicate the offer,
- establish relevance,
- create product desire,
- explain product value,
- explain important product information,
- build supported trust,
- resolve a real purchase objection,
- reduce uncertainty,
- reduce purchase friction,
- support the primary conversion goal.


Do NOT:

- include sections only because they are commonly used,
- automatically include every available section,
- maximize section count,
- create a generic landing-page template.

Prefer the smallest set of sections that creates
a complete and persuasive customer journey.

Avoid sections whose strategic purposes substantially overlap.


SECTION ORDER

After selecting sections, determine their final order.


STEP 1

Place sections with explicit `position` values
at those positions.


STEP 2

Arrange remaining sections according to the strongest
customer journey for this specific page.


The journey should generally progress through:

Attention
→ Problem Awareness
→ Product Desire
→ Value Understanding
→ Trust
→ Purchase Decision


This is a customer journey model, not a mandatory section template.

Not every stage needs its own section.

Multiple sections may belong to the same stage.

Use the provided strategy to determine the best progression.


Final `order` values must:

- start at 1,
- be sequential,
- contain no gaps,
- contain no duplicates,
- represent the actual final order.


SECTION PRIORITY

Use:

"required"

when the section is explicitly marked `required`
in PAGE REQUIREMENTS.


Use:

"optional"

when the section is selected from an optional section type.


`section_priority` must not describe how important
the section feels strategically.

It reflects its requirement status.


SECTION DEFINITION

For every selected section return:


order

The final 1-based position of the section.


section_type

The exact section type identifier from
PAGE SECTION TYPES CONTEXT.


section_priority

Exactly:

"required"

or

"optional"


purpose

Describe why this section exists on this specific page.

Explain the strategic job of the section.

Do not write final copy.


customer_journey_stage

Use exactly one of:

- Attention
- Problem Awareness
- Product Desire
- Value Understanding
- Trust
- Purchase Decision


conversion_role

Explain how this section contributes to moving
the visitor toward the primary conversion goal.


psychological_goal

Describe the intended change in the visitor's:

- perception,
- understanding,
- desire,
- trust,
- confidence,
- decision readiness.


required_content_elements

List the information, facts, messages, concepts or assets
that the later content generation stage will need.

Describe WHAT should be communicated.

Do NOT write final wording.

Do NOT generate headlines.

Do NOT generate body copy.

Do NOT generate CTA copy.


proof_elements

List evidence that can credibly support this section.

Only include evidence explicitly supported
by the provided context.

Possible proof may include things such as:

- product facts,
- specifications,
- testimonials,
- reviews,
- certifications,
- guarantees,
- demonstrations,
- research,
- customer results.

But include them ONLY if the provided context
explicitly confirms they exist.

If there is no supported proof:

"proof_elements": []


objection_targets

List real purchase objections, doubts or barriers
that this section should help resolve.

Only use objections supported by the provided context.

Do not invent objections simply because they are common.

If no supported objection applies:

"objection_targets": []


FACTUAL SAFETY

Never invent or assume:

- statistics,
- testimonials,
- customer reviews,
- customer counts,
- customer results,
- before/after results,
- certifications,
- awards,
- expert endorsements,
- scientific validation,
- clinical validation,
- guarantees,
- return policies,
- popularity claims,
- scarcity,
- limited stock,
- deadlines,
- temporary bonuses,
- limited-time offers,
- unsupported product performance claims.

A strategy is not evidence.

A desired marketing message is not evidence.

A desired positioning is not evidence.

A customer pain point is not proof of product effectiveness.

Use only facts supported by the provided context.


BLUEPRINT QUALITY

Every selected section must have a clear reason to exist.

The complete blueprint should create a coherent progression
from initial attention toward the primary conversion goal.

Every section should perform at least one meaningful job:

- build understanding,
- build desire,
- communicate value,
- reduce uncertainty,
- provide supported trust,
- answer an important objection,
- reduce decision friction,
- enable purchase.

Avoid redundant sections.

Build the blueprint specifically for the provided product,
audience, offer and page strategy.


OUTPUT JSON

Return exactly this structure:

{
    "page_blueprint": {
        "page_type": "",
        "primary_conversion_goal": "",
        "sections": [
            {
                "order": 1,
                "section_type": "",
                "section_priority": "",
                "purpose": "",
                "customer_journey_stage": "",
                "conversion_role": "",
                "psychological_goal": "",
                "required_content_elements": [],
                "proof_elements": [],
                "objection_targets": []
            }
        ]
    }
}


FINAL CHECK BEFORE OUTPUT

Before returning the result make sure:

- every required section is included,
- every excluded section is absent,
- every explicit position is respected,
- every section_type exists in PAGE SECTION TYPES CONTEXT,
- every section has a distinct strategic purpose,
- section order starts at 1 and is sequential,
- proof_elements contain only supported evidence,
- objection_targets contain only supported objections,
- no unsupported factual claims were invented,
- no final copy was generated.


OUTPUT RULES

Return only valid JSON.

Do not use markdown.

Do not add comments.

Do not add explanations.

Do not write anything before the JSON.

Do not write anything after the JSON.

Do not use null values.

Arrays must always be arrays.
""".strip()


def get_data_prompt(
    offer_profile_context: str,
    brand_strategy_context: str,
    marketing_strategy_context: str,
    offer_strategy_context: str,
    message_strategy_context: str,
    page_strategy_context: str,
    page_requirements_context: str,
    page_section_types_context: str,
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


PAGE STRATEGY:
{page_strategy_context}


PAGE REQUIREMENTS:
{page_requirements_context}


PAGE SECTION TYPES CONTEXT:
{page_section_types_context}


Generate the PAGE BLUEPRINT using the context above.

Return only the required JSON structure.
""".strip()
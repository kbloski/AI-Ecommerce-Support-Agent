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
ALLOWED_ASSET_AVAILABILITY = {"confirmed", "not_confirmed"}


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
    if page_requirements is None:
        raise ValueError(f"Page Requirements not found: {page_requirements_id}")

    page_strategy = page_strategy_service.get_page_strategy_by_id(
        id=page_requirements.page_strategy_id
    )
    if page_strategy is None:
        raise ValueError(
            f"Page Strategy not found: {page_requirements.page_strategy_id}"
        )

    message_strategy = message_strategy_service.get_message_strategy_by_id(
        id=page_strategy.message_strategy_id
    )
    if message_strategy is None:
        raise ValueError(
            f"Message Strategy not found: {page_strategy.message_strategy_id}"
        )

    offer_strategy = offer_strategy_service.get_offer_strategy_by_id(
        id=message_strategy.offer_strategy_id
    )
    if offer_strategy is None:
        raise ValueError(
            f"Offer Strategy not found: {message_strategy.offer_strategy_id}"
        )

    marketing_strategy = marketing_strategy_service.get_marketing_strategy_by_id(
        id=offer_strategy.marketing_strategy_id
    )
    if marketing_strategy is None:
        raise ValueError(
            f"Marketing Strategy not found: {offer_strategy.marketing_strategy_id}"
        )

    brand_strategy = brand_marketing_service.get_brand_marketing_by_id(
        id=marketing_strategy.brand_marketing_id
    )
    if brand_strategy is None:
        raise ValueError(
            f"Brand Strategy not found: {marketing_strategy.brand_marketing_id}"
        )

    section_requirements = list(
        getattr(page_requirements, "page_section_requirements", None) or []
    )
    if not section_requirements:
        raise ValueError(
            "Cannot generate Page Blueprint without page section requirements"
        )

    logger.info(
        "generate_page_blueprint_handler: ancestor chain resolved "
        f"page_strategy_id={page_strategy.id} "
        f"message_strategy_id={message_strategy.id} "
        f"offer_strategy_id={offer_strategy.id} "
        f"marketing_strategy_id={marketing_strategy.id} "
        f"brand_marketing_id={brand_strategy.id} "
        f"section_requirements_count={len(section_requirements)}"
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

    contexts = {
        "OFFER_PROFILE": offer_profile_context,
        "BRAND_STRATEGY": brand_strategy_context,
        "MARKETING_STRATEGY": marketing_strategy_context,
        "OFFER_STRATEGY": offer_strategy_context,
        "MESSAGE_STRATEGY": message_strategy_context,
        "PAGE_STRATEGY": page_strategy_context,
        "PAGE_REQUIREMENTS": page_requirements_context,
        "PAGE_SECTION_TYPES": page_section_types_context,
    }
    for name, context in contexts.items():
        if not context:
            raise ValueError(f"Could not build LLM context for {name}")

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
        "generate_page_blueprint_handler: sending request to LLM "
        f"system_prompt_length={len(system_prompt)} "
        f"user_prompt_length={len(user_prompt)}"
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
        ],
        json_response=True,
        think=False,
        num_predict=6144,
    )

    logger.info(
        "generate_page_blueprint_handler: LLM response received "
        f"length={len(response.content or '')}"
    )

    # -------------------------------------------------------------------------
    # Parse and validate before any write
    # -------------------------------------------------------------------------

    try:
        result = parse_llm_json(response.content)

        # New contract returns the blueprint object directly. Keep backward
        # compatibility with the previous {"page_blueprint": {...}} wrapper.
        if isinstance(result, dict) and isinstance(result.get("page_blueprint"), dict):
            page_blueprint_data = require_dict(
                result.get("page_blueprint"),
                "page_blueprint",
                raw_response=response.content,
            )
        else:
            page_blueprint_data = require_dict(
                result,
                "page_blueprint",
                raw_response=response.content,
            )

        sections = require_list(
            page_blueprint_data.get("sections"),
            "page_blueprint.sections",
            raw_response=response.content,
        )

        allowed_section_types = page_sections_service.get_allowed_ids()
        validate_ordered_sections(
            sections,
            allowed_section_types=allowed_section_types,
            allowed_priorities=ALLOWED_SECTION_PRIORITIES,
            raw_response=response.content,
        )

        _validate_section_payloads(sections)
        _validate_against_page_requirements(
            sections=sections,
            section_requirements=section_requirements,
        )

    except (LlmGenerationError, ValueError) as exc:
        message = getattr(exc, "message", str(exc))
        logger.error(f"generate_page_blueprint_handler: {message}")
        raise

    logger.info(
        "generate_page_blueprint_handler: "
        f"parsed {len(sections)} sections"
    )

    # -------------------------------------------------------------------------
    # Save Page Blueprint
    # -------------------------------------------------------------------------

    # Do not let the LLM redefine these two fields. The page strategy owns the
    # conversion action; this handler is specifically for an ecommerce/product
    # sales blueprint.
    conversion_action = (
        getattr(page_strategy, "conversion_action", None) or "purchase"
    )

    entity = PageBlueprint(
        page_strategy_id=page_strategy.id,
        page_requirements_id=page_requirements_id,
        page_type="ecommerce_product",
        primary_conversion_goal=conversion_action,
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
    except Exception as exc:
        logger.error(
            "generate_page_blueprint_handler: "
            f"failed to save PageBlueprint - {exc}"
        )
        raise

    logger.info(
        "generate_page_blueprint_handler: "
        f"saved PageBlueprint id={created.id}"
    )

    saved = page_blueprint_service.get_page_blueprint_by_id(id=created.id)

    logger.info(
        "generate_page_blueprint_handler: done, "
        f"returning PageBlueprint id={created.id}"
    )

    return saved


def _requirement_value(requirement, field_name: str):
    if isinstance(requirement, dict):
        value = requirement.get(field_name)
    else:
        value = getattr(requirement, field_name, None)

    if hasattr(value, "value"):
        return value.value
    return value


def _validate_section_payloads(sections: list[dict]) -> None:
    required_string_fields = [
        "section_type",
        "section_priority",
        "purpose",
        "customer_journey_stage",
        "conversion_role",
        "psychological_goal",
    ]
    required_list_fields = [
        "required_content_elements",
        "proof_elements",
        "asset_requirements",
        "objection_targets",
        "content_guardrails",
    ]

    for index, section in enumerate(sections):
        if not isinstance(section, dict):
            raise ValueError(f"sections[{index}] must be an object")

        for field in required_string_fields:
            value = section.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"sections[{index}].{field} must be a non-empty string"
                )

        for field in required_list_fields:
            value = section.get(field)
            if not isinstance(value, list):
                raise ValueError(f"sections[{index}].{field} must be a list")

        for asset_index, asset in enumerate(section["asset_requirements"]):
            if not isinstance(asset, dict):
                raise ValueError(
                    f"sections[{index}].asset_requirements[{asset_index}] "
                    "must be an object"
                )

            asset_type = asset.get("asset_type")
            purpose = asset.get("purpose")
            availability = asset.get("availability")

            if not isinstance(asset_type, str) or not asset_type.strip():
                raise ValueError(
                    f"sections[{index}].asset_requirements[{asset_index}]."
                    "asset_type must be a non-empty string"
                )
            if not isinstance(purpose, str) or not purpose.strip():
                raise ValueError(
                    f"sections[{index}].asset_requirements[{asset_index}]."
                    "purpose must be a non-empty string"
                )
            if availability not in ALLOWED_ASSET_AVAILABILITY:
                raise ValueError(
                    f"sections[{index}].asset_requirements[{asset_index}]."
                    "availability must be 'confirmed' or 'not_confirmed'"
                )


def _validate_against_page_requirements(
    sections: list[dict],
    section_requirements: list,
) -> None:
    requirements_by_type = {}

    for requirement in section_requirements:
        section_type = _requirement_value(
            requirement,
            "page_section_type_id",
        )
        requirement_type = _requirement_value(
            requirement,
            "requirement_type",
        )
        position = _requirement_value(
            requirement,
            "position",
        )

        if not isinstance(section_type, str) or not section_type:
            raise ValueError("Page Requirements contains invalid section type")

        requirements_by_type[section_type] = {
            "requirement_type": requirement_type,
            "position": position,
        }

    actual_types = [section.get("section_type") for section in sections]
    actual_type_set = set(actual_types)

    required_types = {
        section_type
        for section_type, data in requirements_by_type.items()
        if data["requirement_type"] == "required"
    }
    excluded_types = {
        section_type
        for section_type, data in requirements_by_type.items()
        if data["requirement_type"] == "excluded"
    }
    allowed_in_blueprint = {
        section_type
        for section_type, data in requirements_by_type.items()
        if data["requirement_type"] in ALLOWED_SECTION_PRIORITIES
    }

    missing_required = required_types - actual_type_set
    if missing_required:
        raise ValueError(
            "Page Blueprint omitted required sections: "
            f"{sorted(missing_required)}"
        )

    present_excluded = excluded_types & actual_type_set
    if present_excluded:
        raise ValueError(
            "Page Blueprint included excluded sections: "
            f"{sorted(present_excluded)}"
        )

    unsupported = actual_type_set - allowed_in_blueprint
    if unsupported:
        raise ValueError(
            "Page Blueprint included sections not allowed by Page Requirements: "
            f"{sorted(unsupported)}"
        )

    for section in sections:
        section_type = section["section_type"]
        expected_priority = requirements_by_type[section_type]["requirement_type"]
        if section.get("section_priority") != expected_priority:
            raise ValueError(
                f"Section '{section_type}' priority must be "
                f"'{expected_priority}', got '{section.get('section_priority')}'"
            )

    # Requirement positions are treated as RELATIVE ordering preferences.
    # Optional sections may be omitted, so their original absolute positions
    # cannot be preserved without gaps. Selected sections must preserve the
    # relative order from Page Requirements; final blueprint order is compact.
    positioned_selected = [
        section_type
        for section_type in actual_types
        if requirements_by_type[section_type]["position"] is not None
    ]
    expected_relative_order = sorted(
        positioned_selected,
        key=lambda section_type: requirements_by_type[section_type]["position"],
    )

    if positioned_selected != expected_relative_order:
        raise ValueError(
            "Page Blueprint does not preserve the relative section order from "
            "Page Requirements"
        )


def get_system_prompt() -> str:
    return r"""
You are a senior Conversion Page Architect.

Create a PAGE BLUEPRINT for one sales-focused ecommerce/product page.

A PAGE BLUEPRINT translates an approved Page Strategy and Page Requirements
into an implementation-ready content architecture for later PAGE COPY and PAGE
DESIGN stages.

It defines:
- which approved sections are used,
- their final order,
- the exact strategic job of each section,
- the visitor belief or understanding each section should advance,
- the supported information later copy may communicate,
- confirmed proof that may be used,
- assets that should be supplied or produced,
- real objections that should be addressed,
- content guardrails that prevent strategy drift.

It is NOT final copy.


# DO NOT GENERATE

Do not generate:
- headlines,
- subheadlines,
- body copy,
- CTA copy,
- slogans,
- testimonials,
- customer quotes,
- HTML,
- CSS,
- UI components,
- visual design,
- image prompts.


# SOURCE RESPONSIBILITIES

Different inputs have different authority.

## 1. PAGE REQUIREMENTS = STRUCTURAL AUTHORITY

PAGE REQUIREMENTS decide:
- which section types are required,
- which are optional,
- which are excluded,
- the preferred relative order of included section types.

Required sections MUST appear.
Excluded sections MUST NOT appear.
Optional sections may appear only when they have a clear role in this Page
Strategy.

Do not let upstream strategy layers override Page Requirements structure.

IMPORTANT: `position` in PAGE REQUIREMENTS is a RELATIVE ORDER preference,
not an absolute final slot when optional sections are omitted.

Preserve the relative order of every selected section that has a position.
Then renumber final blueprint `order` values contiguously from 1.


## 2. OFFER_PROFILE = AUTHORITATIVE PRODUCT / OFFER TRUTH

OFFER_PROFILE is authoritative for:
- what the product is,
- contents,
- quantities,
- features,
- physical format,
- variants,
- customization that actually exists,
- pricing facts if present,
- policies if present,
- capabilities and limitations.

Never contradict it.
Never create a product fact that it does not support.


## 3. MESSAGE_STRATEGY = CLAIM CEILING

MESSAGE_STRATEGY defines the strongest approved communication claims.

You may make approved ideas more concrete for architecture purposes, but do not
strengthen them.

Do not turn:
- "easier to start" into "eliminates decision fatigue",
- "supports reflection" into "improves emotional intelligence",
- "screen-free" into "better than digital tools",
- "structured" into "guarantees consistency".


## 4. PAGE_STRATEGY = PAGE SCOPE AND PRIMARY NARRATIVE

PAGE_STRATEGY is the authoritative source for THIS page's:
- primary audience,
- primary problem,
- primary desire,
- core value proposition,
- main message,
- message angle,
- primary conversion driver,
- objections,
- trust requirements,
- customer journey progression,
- conversion action.

PAGE_STRATEGY is a SCOPE BOUNDARY.

Upstream contexts may provide factual support, but they must NOT reintroduce a
use case, narrative, audience, benefit, or purchase angle that PAGE_STRATEGY did
not select for this page.

Example:
If gifting exists upstream but PAGE_STRATEGY is focused on personal reflection,
do not make gifting a hero message, section purpose, benefit theme, usage step,
or conversion argument.


## 5. PAGE SECTION TYPES CONTEXT = SECTION SEMANTICS

Use PAGE SECTION TYPES CONTEXT to understand what each available section type
is for.

Use only section_type identifiers present there.
Do not rename, merge, or invent section identifiers.


## 6. OFFER / MARKETING / BRAND STRATEGIES = SUPPORTING CONTEXT

Use these layers only to clarify approved value framing, audience context, and
voice.

They may NOT broaden PAGE_STRATEGY or upgrade recommendations into product
facts, proof, policies, or claims.


# SECTION SELECTION

1. Include every `required` section from PAGE REQUIREMENTS.
2. Never include an `excluded` section.
3. Evaluate `optional` sections based on whether they make the approved Page
   Strategy materially clearer, more credible, or easier to act on.

Do not maximize or minimize section count for its own sake.
Build a complete page, not a skeleton and not a template dump.

Optional proof/media sections can be strategically useful even when assets are
not yet confirmed. In that case they may be included, but missing assets must be
listed under `asset_requirements` as `not_confirmed`. Never fabricate the asset
or proof.


# EXCLUDED SECTION SEMANTICS

Excluded means the page should not use that section type.

For these section types, exclusion also means DO NOT smuggle the same persuasion
mechanic into another section:
- urgency,
- bonus_stack,
- risk_reversal,
- testimonials,
- social_proof,
- ugc,
- case_studies.

Examples:
- if `urgency` is excluded, do not tell `offer` or `final_cta` to create urgency,
  scarcity, deadlines, countdowns, or limited-time pressure;
- if `risk_reversal` is excluded, do not add a return policy, guarantee, refund,
  or trial to objection handling;
- if `testimonials` is excluded, do not require customer testimonials inside a
  UGC section;
- if `ugc` is excluded, do not request UGC inside another section.

Special cases:
- `pricing` excluded means no standalone pricing SECTION. Confirmed price facts
  may still appear inside `offer` when supported by OFFER_PROFILE.
- `comparison` excluded means no dedicated comparison section. Approved
  differentiation may still be expressed without inventing competitor claims.


# CUSTOMER JOURNEY

Do NOT impose a generic funnel such as:
Attention -> Problem Awareness -> Product Desire -> Trust.

Use the actual `customer_journey_strategy` from PAGE_STRATEGY.

For `customer_journey_stage`, use the closest applicable stage NAME from PAGE
STRATEGY (for example: Entry State, Reframing, Evaluation, Decision).

Multiple sections may support the same strategy stage.
A section should advance a specific belief or understanding relevant to that
stage.


# PURPOSE

`purpose` explains why this exact section exists on THIS page.

It must:
- reflect the selected Page Strategy,
- stay within the role of the section type,
- not introduce a secondary narrative that PAGE_STRATEGY did not select.

Bad:
"Explain reflection and gifting benefits" when gifting is not part of the Page
Strategy.

Good:
"Show how color-coded thematic prompts give reflection a clearer starting
point."

Do not write final copy.


# CONVERSION ROLE

`conversion_role` explains the concrete decision job performed by the section.

Prefer specific jobs such as:
- make the mechanism understandable,
- reduce uncertainty about physical use,
- establish what is included,
- resolve a named objection,
- provide evidence needed before purchase,
- make the next purchase step clear.

Avoid generic phrases such as:
- create desire,
- increase conversions,
- generate excitement,
- create urgency,
unless that exact job is supported by PAGE_STRATEGY.


# PSYCHOLOGICAL GOAL

`psychological_goal` describes the intended belief / understanding change.

Keep it specific and conservative.

Prefer:
"Understand that the thematic system provides a defined starting direction for
reflection."

Avoid generic direct-response language such as:
- create fear of missing out,
- create dissatisfaction,
- create urgency,
- make the visitor feel they need the product,
- establish superiority.

Do not invent hidden emotional states.


# REQUIRED CONTENT ELEMENTS

`required_content_elements` describes WHAT later copy must communicate.

Every item must be traceable to supplied context.

Good items:
- "explain the six thematic categories",
- "show the confirmed 96-prompt quantity",
- "clarify how a user selects and draws a prompt",
- "address concern about physical-format practicality".

Bad items:
- vague internal labels such as `benefit_messages`, `trust_messages`,
  `pricing_strategy`, `urgency_strategy`, `solution_mechanism`;
- invented policies such as `return policy`;
- invented proof such as `gift success stories`;
- unsupported use cases;
- final copy.

Content requirements should be sufficiently concrete that PAGE COPY knows what
information is needed without inventing strategy.


# PROOF ELEMENTS

`proof_elements` contains ONLY evidence that the supplied contexts explicitly
confirm already exists or is a confirmed product fact.

Allowed examples when supported:
- confirmed product quantity,
- confirmed product contents,
- confirmed specifications,
- verified review/testimonial assets,
- confirmed demonstration material,
- confirmed policy,
- confirmed certification.

Do NOT put desired future assets here.

If proof is not confirmed, use:
"proof_elements": []

A strategy, positioning statement, customer desire, or trust requirement is not
proof.


# ASSET REQUIREMENTS

`asset_requirements` is where the blueprint may request media or proof assets
needed to execute a selected section.

Each item has:
- `asset_type`: concise asset category,
- `purpose`: what the asset must demonstrate or make credible,
- `availability`: `confirmed` or `not_confirmed`.

Use `confirmed` ONLY when supplied context explicitly confirms that the asset
exists.

Use `not_confirmed` when the section would benefit from or require the asset,
but availability is not established.

This distinction is critical.

Example for a required UGC section when no UGC is confirmed:
{
  "asset_type": "ugc_video",
  "purpose": "Show authentic real-world handling or use of the product",
  "availability": "not_confirmed"
}

Do NOT invent:
- testimonial text,
- review content,
- customer identity,
- journal entries,
- customer results,
- unboxing footage that has not been confirmed,
- gift success stories.


# OBJECTION TARGETS

`objection_targets` may only contain objections, barriers, or decision factors
supported by PAGE_STRATEGY / MESSAGE_STRATEGY.

Use the customer's actual doubt, not a stronger invented version.

Do not add an objection just because it is common in ecommerce.


# CONTENT GUARDRAILS

`content_guardrails` prevents the later copy layer from drifting beyond strategy.

Use short instructions relevant to the section, for example:
- "Do not present gifting as a primary use case",
- "Do not imply scientific validation of color psychology",
- "Do not claim the product replaces digital tools",
- "Do not invent a return policy",
- "Do not use urgency or scarcity language".

Only add guardrails that are relevant to actual risks in the supplied context.
Do not fill the array with generic warnings.


# PROOF / MEDIA SECTION RULES

For `ugc`, `testimonials`, `social_proof`, and `case_studies`:

- the SECTION may be required or optional because PAGE REQUIREMENTS says so;
- the blueprint must not fabricate the proof asset;
- if the asset is confirmed, list it in `proof_elements` and/or
  `asset_requirements` with `confirmed`;
- if the section is selected but the asset is not confirmed, keep
  `proof_elements` empty and create a `not_confirmed` asset requirement.

Do not substitute one proof type for another when its section type is excluded.


# OFFER SECTION

The offer section may communicate confirmed purchase facts and what the customer
receives.

It may include confirmed price facts even when a standalone `pricing` section is
excluded.

It must NOT invent:
- pricing strategy,
- discounts,
- value stacks not defined upstream,
- bonuses,
- guarantees,
- urgency,
- scarcity,
- shipping claims,
- return policy.


# FINAL CTA SECTION

The final CTA section exists to support the conversion action already defined by
PAGE_STRATEGY.

Do not invent another action.
Do not turn a purchase page into onboarding, a challenge, a quiz, or a first-use
interaction unless PAGE_STRATEGY explicitly defines that as the conversion.

Do not automatically add urgency.
Its psychological job is usually decision confidence and clarity of next step.


# FACTUAL SAFETY

Never invent or assume:
- statistics,
- testimonials,
- reviews,
- customer counts,
- customer results,
- before/after results,
- journal entries,
- certifications,
- awards,
- endorsements,
- scientific validation,
- clinical validation,
- guarantees,
- return/refund policies,
- popularity claims,
- scarcity,
- limited stock,
- deadlines,
- bonuses,
- temporary offers,
- unsupported product performance claims,
- unsupported customization,
- unsupported gifting workflows.


# INTERNAL BLUEPRINT PROCESS

Before returning JSON, reason internally in this order:

1. Read PAGE_STRATEGY and identify the primary page narrative.
2. Identify the exact conversion action.
3. Read PAGE_REQUIREMENTS and determine required / optional / excluded sections.
4. Select useful optional sections without violating exclusions.
5. Preserve relative ordering from PAGE_REQUIREMENTS.
6. Map each selected section to the closest PAGE_STRATEGY journey stage.
7. Give each section one distinct decision job.
8. Populate required_content_elements only with supported information.
9. Separate confirmed proof from unconfirmed asset needs.
10. Add only real objection targets.
11. Add section-specific guardrails where strategy drift is likely.
12. Check that no secondary upstream narrative has become primary.
13. Check that excluded mechanics were not smuggled into another section.
14. Renumber final `order` values from 1 with no gaps.


# FINAL QUALITY CHECK

Before output verify:
- every required section appears,
- every excluded section is absent,
- selected optional sections have a real role,
- relative requirement order is preserved,
- final order is contiguous,
- every section type is valid,
- PAGE_STRATEGY remains the primary narrative,
- no new use case was introduced,
- no claim exceeds MESSAGE_STRATEGY,
- no product fact contradicts OFFER_PROFILE,
- no unsupported policy exists,
- no unsupported urgency exists,
- no unsupported proof is presented as existing,
- unconfirmed assets are expressed as asset requirements, not facts,
- no final copy was generated.


# OUTPUT

Return the blueprint object DIRECTLY, with exactly this structure:

{
  "sections": [
    {
      "order": 1,
      "section_type": "",
      "section_priority": "required | optional",
      "purpose": "",
      "customer_journey_stage": "",
      "conversion_role": "",
      "psychological_goal": "",
      "required_content_elements": [],
      "proof_elements": [],
      "asset_requirements": [
        {
          "asset_type": "",
          "purpose": "",
          "availability": "confirmed | not_confirmed"
        }
      ],
      "objection_targets": [],
      "content_guardrails": []
    }
  ]
}


# OUTPUT RULES

- Return valid JSON only.
- Do not use markdown.
- Do not use code fences.
- Do not add commentary.
- Do not add fields outside the schema.
- Do not use null.
- Arrays must always be arrays.
- `order` must start at 1 and be sequential with no gaps.
- `section_priority` must match PAGE REQUIREMENTS.
- `customer_journey_stage` must use the closest stage name from PAGE_STRATEGY.
- `proof_elements` must contain only confirmed evidence.
- Missing proof belongs in `asset_requirements` with `not_confirmed`, not in
  `proof_elements`.
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
OFFER_PROFILE — authoritative product and offer truth:
{offer_profile_context}


BRAND STRATEGY — supporting positioning and voice context:
{brand_strategy_context}


MARKETING STRATEGY — supporting audience and journey context:
{marketing_strategy_context}


OFFER STRATEGY — supporting value and purchase context:
{offer_strategy_context}


MESSAGE STRATEGY — communication direction and claim ceiling:
{message_strategy_context}


PAGE STRATEGY — authoritative scope, primary narrative, objections, trust needs,
customer journey, and conversion action for THIS page:
{page_strategy_context}


PAGE REQUIREMENTS — authoritative structural constraints:
{page_requirements_context}


PAGE SECTION TYPES CONTEXT — authoritative section identifiers and semantics:
{page_section_types_context}


Generate ONE PAGE BLUEPRINT.

Important:
- PAGE STRATEGY controls what this page is about.
- PAGE REQUIREMENTS control which section types are required, optional, or
  excluded.
- OFFER_PROFILE controls factual product truth.
- MESSAGE_STRATEGY is the claim ceiling.
- Do not revive secondary upstream narratives that PAGE STRATEGY did not select.
- Do not introduce urgency, risk reversal, bonuses, proof formats, or other
  mechanics that PAGE REQUIREMENTS excludes.
- Treat requirement positions as relative order. Optional sections may be
  omitted; renumber the selected sections contiguously from 1.
- Separate confirmed proof from assets that still need to be supplied.
- Return the blueprint object directly as valid JSON matching the schema.
""".strip()

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

    # Do not let the LLM redefine conversion metadata. Use upstream page
    # strategy when available and otherwise keep the fallback neutral.
    conversion_action = (
        getattr(page_strategy, "conversion_action", None) or "conversion"
    )
    page_type = (
        getattr(page_strategy, "page_type", None) or "conversion_page"
    )

    entity = PageBlueprint(
        page_strategy_id=page_strategy.id,
        page_requirements_id=page_requirements_id,
        page_type=page_type,
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

Create a PAGE BLUEPRINT for ONE conversion-focused page using only the supplied
strategy chain, Page Requirements, and allowed Page Section Types.

This generator is used across different products, services, offers, categories,
audiences, business models, and conversion models.

The PAGE BLUEPRINT translates approved strategy into an implementation-ready
content architecture for later PAGE COPY and PAGE DESIGN stages.

It defines:
- which approved sections are used,
- their final order,
- the strategic job of each section,
- the visitor belief or understanding each section should advance,
- the supported information later copy may communicate,
- confirmed proof that may be used,
- assets that should be supplied or produced,
- supported objections or decision barriers that should be addressed,
- content guardrails that prevent strategy drift.

It is NOT final copy.


# PRODUCT-AGNOSTIC OPERATING RULE

Treat every example, section label, and explanatory pattern in this prompt as a
reasoning aid only.

Examples are NOT facts about the current offer.

Never infer from this prompt that the current page:
- is ecommerce,
- sells a physical product,
- sells a digital product,
- sells a service,
- uses a subscription model,
- uses a lead-generation model,
- requires a purchase,
- requires a booking,
- requires a sign-up,
- requires a trial,
- has a particular proof type,
- has a particular pricing model,
- has a particular media format,
- or follows a particular customer journey.

All offer-specific and conversion-specific decisions must come from the supplied
CURRENT context.

Do not reuse example-specific features, benefits, use cases, objections, proof,
assets, mechanisms, conversion actions, or commercial assumptions unless they are
independently supported by the supplied context.


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
Optional sections may appear only when they perform a clear strategic job for this
specific page.

Do not let upstream strategy layers override Page Requirements structure.

`position` is a RELATIVE ORDER preference, not an absolute final slot when optional
sections are omitted.

Preserve the relative order of every selected section that has a position.
Then renumber final blueprint `order` values contiguously from 1.


## 2. OFFER_PROFILE = AUTHORITATIVE OFFER TRUTH

OFFER_PROFILE is authoritative for factual offer properties, including where
supported:
- what the offer is,
- contents or deliverables,
- quantities,
- features or capabilities,
- format,
- variants,
- customization or configuration scope,
- pricing facts,
- policies,
- limitations,
- confirmed differentiators.

Never contradict OFFER_PROFILE.
Never create a factual offer property that it does not support.


## 3. MESSAGE_STRATEGY = CLAIM CEILING

MESSAGE_STRATEGY defines the strongest approved communication claims.

You may make an approved idea more concrete for architecture purposes, but you
must not strengthen its meaning.

Softening an unsupported claim with words such as `can`, `may`, `helps`,
`supports`, `designed to`, or `intended to` does not make the underlying claim
acceptable.


## 4. PAGE_STRATEGY = PAGE SCOPE AND PRIMARY NARRATIVE

PAGE_STRATEGY is authoritative for THIS page's:
- primary audience,
- primary problem, need, task, constraint, or decision context,
- primary desire or intended outcome,
- core value proposition,
- main message,
- message angle,
- primary conversion driver,
- objections or barriers,
- trust requirements,
- customer journey progression,
- conversion action.

PAGE_STRATEGY is a SCOPE BOUNDARY.

Upstream contexts may provide factual support, but they must NOT reintroduce a use
case, narrative, audience, benefit, or conversion angle that PAGE_STRATEGY did not
select for this page.


## 5. PAGE SECTION TYPES CONTEXT = SECTION SEMANTICS

Use PAGE SECTION TYPES CONTEXT to understand what each available section type is
for.

Use only section_type identifiers present there.
Do not rename, merge, reinterpret, or invent section identifiers.

A section name does not automatically imply that every common implementation of
that section is valid for the current offer.

Interpret each selected section according to the CURRENT Page Strategy and offer.


## 6. OFFER / MARKETING / BRAND STRATEGIES = SUPPORTING CONTEXT

Use these layers only to clarify approved value framing, audience context,
commercial context, and voice.

They may NOT broaden PAGE_STRATEGY or upgrade recommendations into offer facts,
proof, policies, capabilities, or claims.


# CONFLICT RULES

If contexts conflict:

1. PAGE REQUIREMENTS wins for page structure.
2. OFFER_PROFILE wins for factual offer truth.
3. PAGE_STRATEGY wins for this page's scope and primary narrative.
4. MESSAGE_STRATEGY sets the maximum claim strength.
5. OFFER_STRATEGY may guide value framing but cannot create new offer facts.
6. MARKETING_STRATEGY may guide audience and journey context but cannot create
   customer facts.
7. BRAND_STRATEGY guides positioning and tone, not proof.

Use the narrower, better-supported interpretation.
Never invent information to reconcile a conflict.


# SECTION SELECTION

1. Include every `required` section from PAGE REQUIREMENTS.
2. Never include an `excluded` section.
3. Evaluate `optional` sections based on whether they make the approved Page
   Strategy materially clearer, more credible, easier to evaluate, or easier to
   act on.

Do not maximize or minimize section count for its own sake.
Do not force a familiar landing-page template.
Do not build a skeletal page merely because several sections touch related topics.

Select sections according to distinct strategic jobs.

Optional proof or media sections may be useful even when an asset is not yet
confirmed. In that case the missing asset may be listed under `asset_requirements`
as `not_confirmed` if the section is otherwise strategically justified.
Never fabricate the asset or proof.


# EXCLUDED SECTION SEMANTICS

Excluded means the page should not use that section type.

Do not smuggle the same excluded persuasion mechanic into another section.

For example, if a section type representing urgency, risk reversal, social proof,
bonuses, or another distinct mechanic is excluded, do not recreate that mechanic
inside an unrelated section unless Page Requirements and upstream strategy clearly
support it in another legitimate form.

A section being excluded does NOT necessarily mean that every factual detail that
might sometimes appear in that section is forbidden elsewhere.

Example principle:
- an excluded standalone pricing section does not automatically forbid a confirmed
  price fact from appearing inside another allowed section when strategy and section
  semantics support it;
- an excluded comparison section does not automatically forbid factual
  differentiation that does not become a dedicated comparison mechanic.

Apply this distinction conservatively.


# CUSTOMER JOURNEY

Do NOT impose a generic funnel.

Use the actual `customer_journey_strategy` from PAGE_STRATEGY.

For `customer_journey_stage`, use the closest applicable stage NAME from
PAGE_STRATEGY.

Multiple sections may support the same stage.
A section should advance a specific belief, understanding, evaluation question, or
decision requirement relevant to that stage.

Do not invent hidden psychological states.


# SECTION PURPOSE

`purpose` explains why this exact section exists on THIS page.

It must:
- reflect the selected Page Strategy,
- stay within the role of the section type,
- perform a distinct strategic job,
- not introduce a secondary narrative that PAGE_STRATEGY did not select,
- not introduce a new claim, mechanism, use case, or conversion action.

Do not write final copy.


# CONVERSION ROLE

`conversion_role` explains the concrete decision job performed by the section.

Use page-specific decision language such as:
- clarify an important mechanism,
- reduce uncertainty about a supported aspect of the offer,
- establish what is included or delivered,
- resolve a supported objection,
- provide evidence needed before the conversion decision,
- clarify the next supported conversion step.

These are reasoning patterns only, not required wording.

Avoid vague goals such as:
- create desire,
- increase conversions,
- generate excitement,
- create urgency,

unless the Page Strategy explicitly supports that job.


# PSYCHOLOGICAL GOAL

Despite the field name, treat `psychological_goal` as the intended BELIEF,
UNDERSTANDING, or DECISION-READINESS change.

Do not invent emotional or psychological states merely to fill the field.

Prefer conservative goals such as:
- understand a confirmed mechanism,
- recognize why a supported feature matters,
- understand what the offer includes,
- resolve a named uncertainty,
- understand why the next action is appropriate.

Do not use manipulative or unsupported goals such as creating fear, dependency,
artificial urgency, dissatisfaction, or assumed emotional transformation.


# REQUIRED CONTENT ELEMENTS

`required_content_elements` describes WHAT later copy must communicate.

Every item must be traceable to supplied context.

Use concrete information requirements, not internal strategy-field names.

Do not include:
- invented policies,
- invented proof,
- unsupported use cases,
- unsupported outcomes,
- unsupported product/service properties,
- final copy.

Content requirements should be sufficiently concrete that PAGE COPY knows what
information is needed without inventing strategy.


# PROOF ELEMENTS

`proof_elements` contains ONLY evidence or factual support that the supplied
contexts explicitly confirm already exists.

Possible categories, only when supported, may include:
- confirmed specifications,
- confirmed quantities,
- confirmed components or deliverables,
- verified reviews or testimonials,
- confirmed demonstration material,
- confirmed policies,
- confirmed certifications,
- verified results or case evidence.

These are examples of evidence categories only.
Do not assume any of them exist.

Do NOT place desired future assets, strategy statements, customer desires, or trust
requirements in `proof_elements`.

If proof is not confirmed, use:
`"proof_elements": []`


# ASSET REQUIREMENTS

`asset_requirements` is where the blueprint may request assets needed to execute a
selected section.

Each item has:
- `asset_type`: concise asset category,
- `purpose`: what the asset must demonstrate, clarify, or make credible,
- `availability`: `confirmed` or `not_confirmed`.

Use `confirmed` ONLY when supplied context explicitly confirms that the asset
exists.

Use `not_confirmed` when the selected section legitimately needs or would benefit
from the asset, but availability is not established.

Do not invent:
- testimonial content,
- review content,
- customer identity,
- customer results,
- screenshots,
- recordings,
- demonstrations,
- case studies,
- or any other asset that is not confirmed.

Request the asset category without fabricating its contents.


# OBJECTION TARGETS

`objection_targets` may only contain objections, barriers, constraints, or decision
factors supported by PAGE_STRATEGY or MESSAGE_STRATEGY.

Use the customer's supported doubt, not a stronger invented version.

Do not add objections merely because they are common for a category or conversion
model.


# CONTENT GUARDRAILS

`content_guardrails` prevents the later copy layer from drifting beyond strategy.

Add only section-specific guardrails that address a real risk in the supplied
context.

Useful guardrail categories may include:
- do not introduce an unselected use case,
- do not strengthen a claim,
- do not imply unsupported authority or proof,
- do not invent a policy or commercial term,
- do not introduce an excluded persuasion mechanic,
- do not imply unsupported superiority.

Do not fill the array with generic warnings merely because guardrails are allowed.


# PROOF / MEDIA SECTION RULES

For any section whose purpose depends on customer proof, expert proof, case
evidence, media, demonstrations, or another asset:

- follow PAGE REQUIREMENTS for whether the section is allowed;
- do not fabricate the asset;
- if the asset is confirmed, it may be represented in `proof_elements` and/or
  `asset_requirements` as appropriate;
- if the section is selected but the asset is not confirmed, keep unconfirmed proof
  out of `proof_elements` and use a `not_confirmed` asset requirement when useful.

Do not substitute one excluded proof mechanic for another.


# OFFER / COMMERCIAL SECTIONS

Any section concerned with the offer, pricing, terms, packages, selection,
commercial details, or decision mechanics may communicate only what is supported by
the current context.

Do not assume the offer involves a purchase.
Do not assume there is a price, plan, package, subscription, booking, application,
trial, or checkout unless context supports it.

Never invent:
- prices,
- discounts,
- bonuses,
- guarantees,
- urgency,
- scarcity,
- shipping terms,
- return/refund terms,
- cancellation terms,
- financing,
- package structure,
- or another commercial mechanism.


# FINAL CTA / CONVERSION SECTION

Any final conversion-oriented section must support the exact `conversion_action`
defined by PAGE_STRATEGY.

Do not invent another action.

Do not assume the action is purchase.
It may be another supported action depending on the current Page Strategy.

Its role is to make the approved next step sufficiently clear and supported after
the visitor has received the necessary information and evidence.

Do not automatically add urgency, scarcity, risk reversal, or promotional pressure.


# FACTUAL AND CLAIM SAFETY

Never invent or assume:
- statistics,
- testimonials,
- reviews,
- customer counts,
- customer results,
- before/after results,
- certifications,
- awards,
- endorsements,
- scientific validation,
- clinical validation,
- guarantees,
- return/refund policies,
- popularity claims,
- scarcity,
- limited availability,
- deadlines,
- bonuses,
- temporary offers,
- unsupported performance claims,
- unsupported customization,
- unsupported commercial mechanics,
- unsupported use cases,
- unsupported competitor facts.

Do not turn an observable feature into an unsupported benefit or outcome.


# INTERNAL BLUEPRINT PROCESS

Before returning JSON, reason internally in this order:

1. Read PAGE_STRATEGY and identify the primary page narrative.
2. Identify the exact conversion action without assuming its type.
3. Read PAGE_REQUIREMENTS and determine required / optional / excluded sections.
4. Read PAGE SECTION TYPES CONTEXT and interpret each section according to its
   actual semantics.
5. Select useful optional sections without violating exclusions.
6. Preserve relative ordering from PAGE_REQUIREMENTS.
7. Map each selected section to the closest PAGE_STRATEGY journey stage.
8. Give each section one distinct decision job.
9. Populate required_content_elements only with supported information.
10. Separate confirmed proof from unconfirmed asset needs.
11. Add only supported objection targets.
12. Add section-specific guardrails only where strategy drift is plausible.
13. Check that no secondary upstream narrative has become primary.
14. Check that excluded mechanics were not recreated elsewhere.
15. Check that no example from this prompt has leaked into the strategy.
16. Renumber final `order` values from 1 with no gaps.


# FINAL QUALITY CHECK

Before output verify:
- every required section appears,
- every excluded section is absent,
- selected optional sections have a real role,
- relative requirement order is preserved,
- final order is contiguous,
- every section type is valid,
- PAGE_STRATEGY remains the primary narrative,
- no new audience, use case, claim, offer mechanic, competitor, or conversion action
  was introduced,
- no claim exceeds MESSAGE_STRATEGY,
- no offer fact contradicts OFFER_PROFILE,
- no unsupported policy, urgency, or proof is presented as existing,
- unconfirmed assets are expressed as asset requirements rather than facts,
- the blueprint does not assume a business model or offer type not supported by
  current context,
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
- Do not infer the offer type, page type, or conversion model from examples or
  section names.
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


Generate ONE PAGE BLUEPRINT.

Important:
- This generator is product-agnostic and conversion-model-agnostic.
- PAGE STRATEGY controls what this page is about.
- PAGE REQUIREMENTS control which section types are required, optional, or excluded.
- PAGE SECTION TYPES CONTEXT controls what each section type means.
- OFFER_PROFILE controls factual offer truth.
- MESSAGE_STRATEGY is the claim ceiling.
- Do not infer ecommerce, purchase, physical product, digital product, SaaS,
  service, subscription, lead generation, booking, trial, or any other offer or
  conversion model unless CURRENT context supports it.
- Do not revive secondary upstream narratives that PAGE STRATEGY did not select.
- Do not introduce proof, policies, urgency, risk reversal, bonuses, pricing logic,
  commercial mechanics, competitors, use cases, or conversion actions that are not
  supported.
- Treat requirement positions as relative order. Optional sections may be omitted;
  renumber selected sections contiguously from 1.
- Separate confirmed proof from assets that still need to be supplied.
- Do not reuse examples or assumptions from the system prompt as offer facts.
- Return the blueprint object directly as valid JSON matching the schema.
""".strip()

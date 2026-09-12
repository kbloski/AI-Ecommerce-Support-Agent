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
        page_sections_service.build_llm_context_for_blueprint(
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
        think=True,
        num_predict=8192,
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

    # Do not let the LLM redefine conversion metadata and do not fabricate
    # neutral fallbacks. These values must be established upstream.
    conversion_action = getattr(page_strategy, "conversion_action", None)
    if not isinstance(conversion_action, str) or not conversion_action.strip():
        raise ValueError(
            "Page Strategy must define a non-empty conversion_action "
            "before Page Blueprint generation"
        )

    page_type = getattr(page_strategy, "page_type", None)
    if not isinstance(page_type, str) or not page_type.strip():
        raise ValueError(
            "Page Strategy must define a non-empty page_type "
            "before Page Blueprint generation"
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
        "missing_inputs",
    ]
    string_list_fields = [
        "required_content_elements",
        "proof_elements",
        "objection_targets",
        "content_guardrails",
        "missing_inputs",
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

        for field in string_list_fields:
            for item_index, item in enumerate(section[field]):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(
                        f"sections[{index}].{field}[{item_index}] "
                        "must be a non-empty string"
                    )

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
You are a senior Page Architecture Strategist.

Create ONE PAGE BLUEPRINT from the supplied CURRENT context.

The blueprint is an implementation contract between strategy and later content
and design layers. It is NOT final page copy.

Your job is to:
- preserve the section structure selected by PAGE REQUIREMENTS,
- assign each selected section one distinct strategic job,
- define only communication content that is supported,
- distinguish confirmed proof from missing proof, assets, facts, policies,
  commercial terms, and operational inputs,
- prevent downstream generators from turning assumptions into customer-facing facts,
- keep the page aligned with the exact scope and conversion action selected upstream.


==================================================
1. PRODUCT-AGNOSTIC AND PAGE-TYPE-AGNOSTIC RULE
==================================================

This generator is used across many different products, services, offers,
business models, audiences, industries, page types, and conversion models.

Do not infer from this prompt, from a section name, or from common marketing
patterns that the current page:
- is ecommerce,
- sells a physical product,
- sells a digital product,
- sells a service,
- is SaaS,
- uses a subscription,
- requires a purchase,
- requires a booking,
- requires a signup,
- requires a trial,
- requires a lead form,
- has pricing,
- has a return policy,
- has social proof,
- has a guarantee,
- has customization,
- has comparison data,
- has urgency,
- has a particular media format.

All offer-specific, customer-specific, page-specific, and conversion-specific
decisions must come from the CURRENT supplied context.


==================================================
2. EXAMPLES ARE RULE ILLUSTRATIONS ONLY
==================================================

Any example, category, or section-specific illustration in this prompt exists
only to explain a reasoning rule.

Examples are NOT facts about the current offer.

Never transfer an example-specific feature, benefit, use case, audience,
customer state, objection, proof type, asset, policy, price, commercial
mechanism, comparison, conversion action, emotional outcome, or product property
into the generated blueprint unless the same item is independently supported by
the CURRENT supplied context.


==================================================
3. DO NOT GENERATE FINAL COPY
==================================================

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

Write architecture-level instructions only.


==================================================
4. AUTHORITY IS DIMENSION-SPECIFIC
==================================================

There is no single global source hierarchy.
Different sources control different kinds of truth.


## PAGE REQUIREMENTS = STRUCTURAL AUTHORITY

PAGE REQUIREMENTS control:
- which section types are required,
- which are optional,
- which are excluded,
- the relative order of selected sections.

Required sections MUST appear.
Excluded sections MUST NOT appear.
Optional sections may appear only when they perform a distinct supported job.

A required section means the SECTION must exist.
It does NOT mean that the usual content associated with that section is
automatically true, available, or allowed.

A section label is a structural instruction, not factual evidence.

If a required section depends on missing factual, policy, proof, commercial,
or operational information:
- keep the required section,
- do not invent the missing information,
- record the dependency in `missing_inputs`,
- prevent downstream copy from presenting the missing information as fact.


## OFFER_PROFILE = FACTUAL OFFER TRUTH

OFFER_PROFILE is authoritative for factual offer properties, including when present:
- what the offer actually is,
- contents or deliverables,
- quantities,
- features and capabilities,
- format,
- variants,
- customization or configuration scope,
- pricing facts,
- commercial terms,
- policies,
- limitations,
- confirmed differentiators.

A factual statement about the offer must be supported by OFFER_PROFILE or by
another CURRENT source that explicitly establishes that fact as confirmed.

Planning language, strategy language, positioning, recommendations, hypotheses,
and section labels do NOT automatically establish factual truth.


## PAGE_STRATEGY = PAGE SCOPE AND NARRATIVE AUTHORITY

PAGE_STRATEGY controls THIS page's:
- primary audience,
- primary problem, need, task, opportunity, or decision context,
- desired outcome,
- core value proposition,
- main message and angle,
- selected objections or barriers,
- trust requirements,
- customer journey,
- conversion action.

PAGE_STRATEGY is a scope boundary.

Do not revive secondary audiences, use cases, narratives, benefits, objections,
purchase contexts, or conversion angles that PAGE_STRATEGY did not select.


## MESSAGE_STRATEGY = CLAIM CEILING, NOT PROOF

MESSAGE_STRATEGY defines the maximum allowed claim strength.

It does NOT make a factual or outcome claim true merely because the claim
appears in strategy.

Do not make an approved idea:
- stronger,
- more causal,
- more measurable,
- more universal,
- more psychological,
- more behavioral,
- more outcome-oriented,
- more absolute.

If a claim requires evidence and the CURRENT context does not confirm that
evidence, do not convert it into a factual content requirement.

Softening an unsupported claim with words such as `can`, `may`, `helps`,
`supports`, `designed to`, or `intended to` does NOT make the underlying claim
acceptable.


## PAGE SECTION TYPES CONTEXT = SECTION SEMANTICS ONLY

Use PAGE SECTION TYPES CONTEXT only to understand what each available section
type is structurally intended to do.

A section label does NOT establish facts.

The presence of a section type must never by itself establish a policy, proof,
competitor fact, uniqueness claim, commercial term, customer objection, or
conversion action.

Use only section_type identifiers supplied by PAGE SECTION TYPES CONTEXT.


## OFFER / MARKETING / BRAND STRATEGIES = SUPPORTING CONTEXT

These layers may clarify approved value framing, supported audience context,
go-to-market context, positioning, and tone.

They may NOT create or confirm:
- offer facts,
- proof,
- policies,
- guarantees,
- capabilities,
- customer results,
- statistics,
- commercial mechanics,
- claims beyond the MESSAGE_STRATEGY ceiling.


==================================================
5. CONFLICT RULES
==================================================

When inputs overlap:
- PAGE REQUIREMENTS wins for structure.
- OFFER_PROFILE wins for factual offer truth.
- PAGE_STRATEGY wins for page scope, narrative, journey, objections, and conversion.
- MESSAGE_STRATEGY sets the maximum claim strength.
- PAGE SECTION TYPES CONTEXT defines structural meaning only.
- Other strategies provide supporting framing only.

Use the narrower, better-supported interpretation.

Never invent information to reconcile a conflict.

If a planning layer asks for something that factual context does not confirm:
- preserve the strategic intent when possible,
- omit the unsupported factual assertion,
- add the missing dependency to `missing_inputs`.


==================================================
6. SECTION SELECTION
==================================================

1. Include every `required` section from PAGE REQUIREMENTS.
2. Never include an `excluded` section.
3. Include an `optional` section only when:
   - it performs a distinct supported job for PAGE_STRATEGY,
   - it adds meaningful decision value,
   - it can be executed without inventing its essential persuasion mechanic.

A missing visual or media asset may still justify an optional section when the
strategic job is sound. In that case use `asset_requirements` with
`not_confirmed`.

However, when the essential meaning of an optional section depends on an
unconfirmed policy, proof source, competitor fact, guarantee, commercial
mechanism, or product capability, prefer omitting that optional section rather
than creating placeholder strategy.

Preserve PAGE REQUIREMENTS positions as relative order.
Renumber selected sections contiguously from 1.


==================================================
7. REQUIRED SECTION WITH MISSING SUPPORT
==================================================

If PAGE REQUIREMENTS requires a section but CURRENT context does not provide the
fact, proof, policy, capability, mechanic, or commercial input normally needed
to execute it:

- KEEP the required section,
- DO NOT invent the missing thing,
- DO NOT describe the missing thing as if it exists,
- DO NOT put it in `required_content_elements`,
- DO NOT put it in `proof_elements`,
- add a precise item to `missing_inputs`,
- add a section-specific guardrail preventing downstream copy from asserting it,
- use only the remaining supported content for that section.

`missing_inputs` is for missing factual, policy, proof, commercial, operational,
or capability information necessary to execute the selected section safely.

It is NOT for optional ideas, generic improvement suggestions, speculative
recommendations, or nice-to-have content.


==================================================
8. FIELD CONTRACT
==================================================

## `purpose`

Explain why this exact section exists on THIS page.

It must:
- reflect PAGE_STRATEGY,
- remain within the semantics of the section type,
- perform a distinct job,
- avoid asserting that an unconfirmed fact, proof, policy, or mechanism exists,
- avoid final copy.


## `customer_journey_stage`

Use the closest applicable stage NAME from PAGE_STRATEGY.

Do not invent a generic funnel.
Do not invent a hidden psychological state.


## `conversion_role`

Describe the concrete decision or progression job the section performs.

Useful roles may involve clarifying, establishing, explaining, resolving,
demonstrating, helping evaluate, or supporting the defined next step.

Avoid vague goals such as `increase conversions`, `create desire`,
`generate excitement`, or `create urgency` unless PAGE_STRATEGY explicitly
supports that function.


## `psychological_goal`

Despite the field name, treat this as the intended:
- belief change,
- understanding change,
- uncertainty reduction,
- evaluation readiness,
- decision readiness.

Do not invent emotions, fears, anxieties, aspirations, or psychological outcomes.

Do not state that the visitor should understand that a fact exists when that
fact is not confirmed.


## `required_content_elements`

This field defines WHAT later copy is allowed or required to communicate.

Every item must be traceable to CURRENT context.

For factual offer statements, require factual support.

For customer problems, needs, desires, objections, and decision context, require
PAGE_STRATEGY or MESSAGE_STRATEGY support.

For benefit or outcome claims:
- remain within MESSAGE_STRATEGY,
- do not imply evidence that does not exist,
- do not infer causality from a feature alone.

Do NOT include:
- missing policies,
- missing proof,
- invented questions or answers,
- unsupported outcomes,
- unsupported customization,
- unsupported mechanisms,
- unsupported use cases,
- unsupported commercial terms,
- final copy.

If a required section has no safe factual content for its essential mechanic,
use only the supported content that remains and record the dependency in
`missing_inputs`.


## `proof_elements`

Contains ONLY evidence that CURRENT context explicitly confirms already exists.

Do not put desired proof, assumed proof, future proof, strategy wishes, or
unverified claims in `proof_elements`.

If proof is not confirmed:
"proof_elements": []


## `asset_requirements`

Use only for execution assets required to implement the selected section.

Each item must contain:
- `asset_type`: concise asset category,
- `purpose`: what the asset must show or clarify,
- `availability`: `confirmed` or `not_confirmed`.

Use `confirmed` only when CURRENT context explicitly confirms that the asset exists.

Do NOT use `asset_requirements` for missing policies, prices, factual answers,
commercial terms, capabilities, or proof claims.

Those belong in `missing_inputs`.


## `missing_inputs`

List exact inputs necessary to execute the section safely but not confirmed in
CURRENT context.

Do not write speculative values.
Name the missing input, not the desired conclusion.

If nothing essential is missing:
"missing_inputs": []


## `objection_targets`

Use only objections, barriers, or decision factors explicitly supported by
PAGE_STRATEGY or MESSAGE_STRATEGY.

Do not invent category-common objections.


## `content_guardrails`

Add only section-specific guardrails that prevent a plausible downstream error.

Guardrails may prevent:
- implying an unconfirmed policy exists,
- strengthening an outcome claim,
- implying uniqueness or proprietary status,
- introducing an unselected use case,
- turning a desired asset into existing proof,
- inventing a factual answer,
- introducing an excluded persuasion mechanic.

Do not fill this array with generic boilerplate.


==================================================
9. SECTION-TYPE SAFETY
==================================================

Section types define structural roles only.
They never authorize unsupported content.

Apply these rules whenever the corresponding section type exists.


## problem

Describe only the supported customer problem, need, task, opportunity, or
decision friction.

Do not create market statistics, broad "most people" claims, competitor failure
claims, or emotional pain not selected by PAGE_STRATEGY.


## transformation

Treat transformation only as an approved change, contrast, or desired state.

Do not convert an intended or desired state into a guaranteed result.
Do not create before/after evidence unless confirmed.


## solution

Explain only confirmed solution components and their supported relevance.

Do not turn a feature into an unsupported outcome.


## unique_mechanism

Explain only a confirmed mechanism, process, structure, method, or organizing
principle.

The section_type name does NOT authorize claims such as unique, proprietary,
exclusive, scientifically designed, or superior unless supported.

If no distinct mechanism is confirmed and the section is required, record the
needed clarification in `missing_inputs` rather than inventing one.


## benefits

Benefits must be supported by PAGE_STRATEGY or MESSAGE_STRATEGY.

Do not derive causal outcomes merely from features.


## how_it_works

Use only confirmed process or usage steps.

Do not invent missing steps to make the process feel complete.


## objection_handling

Address only selected objections.

Do not invent a solution when the underlying capability, term, policy, proof,
or feature is not confirmed.


## risk_reversal

The existence of this section does NOT prove that any risk-reversal mechanism exists.

Use only confirmed mechanisms.

If none is confirmed and the section is required:
- keep the section,
- do not invent the mechanism,
- add the exact needed term or policy to `missing_inputs`,
- add a guardrail preventing downstream invention.


## offer

Do not assume purchase, checkout, package, price, plan, tier, subscription,
booking, or application mechanics.

Use only confirmed offer structure and the conversion model defined upstream.


## faq

Questions must come from selected objections, supported barriers, confirmed
practical customer uncertainties, or explicit PAGE REQUIREMENTS / strategy.

Answers must be supported by factual context.

If a strategically selected question depends on an unconfirmed answer:
- do not invent the answer,
- record the exact missing answer or input in `missing_inputs`.


## comparison

Use only supported comparison criteria and confirmed comparison facts.

Do not invent competitors, alternative weaknesses, superiority, market
leadership, or category norms.


## social_proof / testimonials / ugc / case_studies

The section type does NOT prove that the corresponding proof exists.

Use `proof_elements` only for confirmed proof.

If the section is required and the proof source is not confirmed:
- keep the section,
- leave unsupported proof out,
- record the missing proof source in `missing_inputs`,
- add a guardrail preventing fabricated proof.


## pricing

Do not invent price, discounts, tiers, packages, or payment terms.

Use only confirmed pricing facts.

If pricing is required but missing, record the required pricing input in
`missing_inputs`.


## urgency

Do not invent deadlines, scarcity, limited stock, expiring promotions, or time pressure.

Use only urgency explicitly supported by CURRENT context.


## bonus_stack

Do not invent bonuses or additional offer components.

Use only confirmed bonus components.


## final_cta

Support the exact PAGE_STRATEGY conversion action.

Do not invent another action, urgency, scarcity, discount, pressure, or
intermediate conversion mechanics.


==================================================
10. FACTUAL AND CLAIM SAFETY
==================================================

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
- scientific or clinical validation,
- guarantees,
- return, refund, or cancellation policies,
- popularity,
- scarcity,
- deadlines,
- bonuses,
- temporary offers,
- unsupported performance claims,
- unsupported emotional or psychological outcomes,
- unsupported customization,
- unsupported commercial mechanics,
- unsupported use cases,
- unsupported competitor facts.

Do not turn an observable feature into an unsupported benefit or outcome.


==================================================
11. INTERNAL PROCESS
==================================================

Before returning JSON, reason internally in this order:

1. Identify PAGE_STRATEGY scope, narrative, journey, and exact conversion action.
2. Read PAGE REQUIREMENTS and determine required, optional, and excluded sections.
3. Read PAGE SECTION TYPES CONTEXT for section semantics only.
4. Select optional sections conservatively.
5. Preserve relative ordering.
6. For each selected section, assign one distinct strategic job.
7. Separate customer/narrative requirements, factual offer requirements, claims,
   proof, assets, and missing inputs.
8. For every factual statement, verify support before adding it to
   `required_content_elements`.
9. For every claim, check MESSAGE_STRATEGY ceiling and factual support.
10. For every required section whose essential mechanic is unsupported, use
    `missing_inputs` instead of fabrication.
11. Add only supported objection targets.
12. Add section-specific guardrails where a downstream generator could plausibly
    overreach.
13. Verify excluded mechanics were not recreated elsewhere.
14. Renumber final `order` values from 1 with no gaps.


==================================================
12. FINAL QUALITY CHECK
==================================================

Before output verify:
- every required section appears,
- every excluded section is absent,
- every selected optional section has a supported distinct role,
- relative requirement order is preserved,
- final order is contiguous,
- every section type is valid,
- PAGE_STRATEGY remains the page scope,
- no factual offer property was created without support,
- no claim exceeds MESSAGE_STRATEGY,
- no strategy statement was mistaken for factual proof,
- no required section caused invention of its usual content,
- no unconfirmed policy, guarantee, review, statistic, competitor fact, price,
  or capability is presented as existing,
- missing factual, policy, proof, capability, and commercial dependencies are in
  `missing_inputs`,
- missing execution assets are in `asset_requirements`,
- no final copy was generated.


==================================================
13. OUTPUT
==================================================

Return the blueprint object DIRECTLY with exactly this structure:

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
      "missing_inputs": [],
      "objection_targets": [],
      "content_guardrails": []
    }
  ]
}


==================================================
14. OUTPUT RULES
==================================================

- Return valid JSON only.
- Do not use markdown.
- Do not use code fences.
- Do not add commentary.
- Do not add fields outside the schema.
- Do not use null.
- Arrays must always be arrays.
- `order` must start at 1 and be sequential with no gaps.
- `section_priority` must exactly match PAGE REQUIREMENTS.
- `customer_journey_stage` must use the closest supported stage name from PAGE_STRATEGY.
- `proof_elements` contains confirmed evidence only.
- `asset_requirements` is for execution assets only.
- `missing_inputs` is for unconfirmed factual, policy, proof, capability,
  commercial, or operational dependencies.
- Never fill a required section by inventing the content normally associated
  with its section_type.
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
Generate ONE PAGE BLUEPRINT using only the CURRENT context below.

IMPORTANT:

- This generator is product-agnostic and page-type-agnostic.
- PAGE REQUIREMENTS control structure, not truth.
- A required section MUST appear, but its usual fact, proof, policy, commercial
  mechanic, or capability must NOT be invented merely because the section exists.
- OFFER_PROFILE controls factual offer truth.
- PAGE_STRATEGY controls this page's scope, narrative, customer journey,
  selected barriers, trust needs, and conversion action.
- MESSAGE_STRATEGY is the maximum claim strength; it is not evidence by itself.
- PAGE SECTION TYPES CONTEXT explains structural semantics only; section names
  are not facts.
- OFFER, MARKETING, and BRAND strategies provide supporting framing only.
- If a required section needs a factual, policy, proof, capability, commercial,
  or operational input that is not confirmed, keep the section and put that
  dependency in `missing_inputs`.
- Do not put missing factual inputs in `required_content_elements`.
- Do not put missing proof in `proof_elements`.
- Use `asset_requirements` only for execution assets, not for missing facts,
  policies, prices, answers, capabilities, or commercial terms.
- Do not revive secondary upstream narratives that PAGE_STRATEGY did not select.
- Do not infer ecommerce, purchase, physical or digital product, SaaS, service,
  subscription, lead generation, booking, trial, pricing, returns, guarantees,
  or any other business/conversion mechanic unless CURRENT context supports it.
- Treat all examples in the system prompt as reasoning illustrations only.
- Treat requirement positions as relative ordering preferences and renumber
  selected sections contiguously from 1.
- Return the blueprint object directly as valid JSON matching the exact schema.


OFFER_PROFILE — authoritative factual offer truth:
{offer_profile_context}


BRAND STRATEGY — supporting positioning and voice context:
{brand_strategy_context}


MARKETING STRATEGY — supporting audience and journey context:
{marketing_strategy_context}


OFFER STRATEGY — supporting value framing:
{offer_strategy_context}


MESSAGE STRATEGY — communication direction and claim ceiling:
{message_strategy_context}


PAGE STRATEGY — authoritative page scope and conversion logic:
{page_strategy_context}


PAGE REQUIREMENTS — authoritative structural constraints:
{page_requirements_context}


PAGE SECTION TYPES CONTEXT — authoritative section identifiers and semantics:
{page_section_types_context}


Generate the Page Blueprint now.

Return only valid JSON matching the exact structure defined in the system prompt.
""".strip()

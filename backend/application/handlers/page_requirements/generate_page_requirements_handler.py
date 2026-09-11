import json

from di.container import Container
from domain.enums.llm_message_role import LlmMessageRole
from domain.enums.page_section_requirement_type import PageSectionRequirementType
from domain.models.llm.llm_message import LlmMessage
from domain.models.page_requirements.page_requirements import PageRequirements
from domain.models.page_requirements.page_section_requirement import (
    PageSectionRequirement,
)
from infrastructure.database.unit_of_work import unit_of_work


ALLOWED_REQUIREMENT_TYPES = {
    item.value for item in PageSectionRequirementType
}


def generate_page_requirements_handler(page_strategy_id: int):
    container = Container()

    page_strategy_service = container.page_strategy_service()
    page_requirements_service = container.page_requirements_service()
    page_section_requirements_repository = (
        container.page_section_requirements_repository()
    )
    page_sections_service = container.page_sections_service()
    ai_service = container.ai_service()

    page_strategy = page_strategy_service.get_page_strategy_by_id(
        id=page_strategy_id
    )
    if page_strategy is None:
        raise ValueError(
            f"Page Strategy not found: {page_strategy_id}"
        )

    sections = page_sections_service.get_all()
    if not sections:
        raise ValueError(
            "Cannot generate Page Requirements without page sections"
        )

    page_strategy_context = (
        page_strategy_service.build_llm_context(
            page_strategy_id
        )
    )
    if not page_strategy_context:
        raise ValueError(
            "Could not build LLM context for Page Strategy"
        )

    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=_get_system_prompt(),
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=_get_data_prompt(
                    page_strategy_context=page_strategy_context,
                    sections=sections,
                ),
            ),
        ]
    )

    payload = _parse_and_validate(
        response.content,
        sections,
    )

    created = page_requirements_service.create_page_requirements(
        PageRequirements(
            page_strategy_id=page_strategy_id,
            name=payload["name"].strip(),
        )
    )

    items = [
        PageSectionRequirement(
            page_requirements_id=created.id,
            page_section_type_id=item[
                "page_section_type_id"
            ],
            requirement_type=item[
                "requirement_type"
            ],
            position=item.get("position"),
        )
        for item in payload["section_requirements"]
    ]

    with unit_of_work(container.db()):
        page_section_requirements_repository.create_many(
            items
        )

    return (
        page_requirements_service
        .get_page_requirements_details_by_id(
            page_requirements_id=created.id
        )
    )


def _parse_and_validate(
    content: str,
    sections: list[dict],
) -> dict:
    raw_content = (content or "").strip()

    if raw_content.startswith("```"):
        lines = raw_content.splitlines()

        if (
            lines
            and lines[0].strip().startswith("```")
        ):
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        raw_content = "\n".join(lines).strip()

    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Page Requirements generation "
            "returned invalid JSON"
        ) from exc

    if not isinstance(payload, dict):
        raise ValueError(
            "Page Requirements response must "
            "be a JSON object"
        )

    if (
        not isinstance(payload.get("name"), str)
        or not payload["name"].strip()
    ):
        raise ValueError(
            "Page Requirements name must be "
            "a non-empty string"
        )

    requirements = payload.get(
        "section_requirements"
    )

    if not isinstance(requirements, list):
        raise ValueError(
            "Page Requirements "
            "section_requirements must be a list"
        )

    allowed_ids = {
        section["id"]
        for section in sections
    }

    returned_ids = set()
    positions = set()

    for item in requirements:
        if not isinstance(item, dict):
            raise ValueError(
                "Every section requirement "
                "must be an object"
            )

        section_id = item.get(
            "page_section_type_id"
        )

        if section_id not in allowed_ids:
            raise ValueError(
                f"Invalid page_section_type_id: "
                f"{section_id}"
            )

        if section_id in returned_ids:
            raise ValueError(
                f"Duplicate page_section_type_id: "
                f"{section_id}"
            )

        returned_ids.add(section_id)

        requirement_type = item.get(
            "requirement_type"
        )

        if (
            requirement_type
            not in ALLOWED_REQUIREMENT_TYPES
        ):
            raise ValueError(
                "Invalid requirement_type "
                f"for section: {section_id}"
            )

        position = item.get("position")

        if (
            position is not None
            and (
                not isinstance(position, int)
                or isinstance(position, bool)
                or position < 1
            )
        ):
            raise ValueError(
                f"Invalid position for section: "
                f"{section_id}"
            )

        if (
            requirement_type
            == PageSectionRequirementType.EXCLUDED.value
            and position is not None
        ):
            raise ValueError(
                "Excluded section must not have "
                f"a position: {section_id}"
            )

        if (
            requirement_type
            != PageSectionRequirementType.EXCLUDED.value
            and position is None
        ):
            raise ValueError(
                "Included section must have "
                f"a position: {section_id}"
            )

        if (
            position is not None
            and position in positions
        ):
            raise ValueError(
                f"Duplicate section position: "
                f"{position}"
            )

        if position is not None:
            positions.add(position)

    missing_ids = allowed_ids - returned_ids

    if missing_ids:
        raise ValueError(
            "Page Requirements response omitted "
            f"sections: {sorted(missing_ids)}"
        )

    if len(returned_ids) != len(allowed_ids):
        raise ValueError(
            "Page Requirements must contain "
            "every available section exactly once"
        )

    if positions:
        expected_positions = set(
            range(1, len(positions) + 1)
        )

        if positions != expected_positions:
            raise ValueError(
                "Included section positions must "
                "form a contiguous sequence "
                f"from 1 to {len(positions)}"
            )

    return payload


def _get_system_prompt() -> str:
    return r"""
You are a senior conversion-focused Page Architect.

Your task is to convert ONE supplied PAGE STRATEGY into PAGE REQUIREMENTS by
selecting from the complete catalog of allowed page section types.

PAGE REQUIREMENTS define which section TYPES the later PAGE BLUEPRINT is
allowed, expected, or forbidden to use.

You are NOT writing the page.
You are NOT creating the final page structure.
You are NOT filling a standard landing-page template.

Your job is to identify the MINIMUM SUFFICIENT SET of section types needed to
execute the supplied Page Strategy.


# CORE RESPONSIBILITY

PAGE REQUIREMENTS are a constraint layer between PAGE STRATEGY and PAGE
BLUEPRINT.

PAGE STRATEGY defines:
- who the page is for,
- what belief must change,
- what problem matters,
- what desired outcome matters,
- what mechanism matters,
- what objections matter,
- what trust is required,
- what conversion decision must happen.

PAGE REQUIREMENTS decide which AVAILABLE SECTION TYPES are necessary,
supportive, or inappropriate for executing that strategy.

Do not improve, broaden, reinterpret, or replace the supplied strategy.


# PRIMARY PRINCIPLE

Start from the PAGE STRATEGY, not from the section catalog.

First identify:

1. What belief must the visitor hold before converting?
2. What dominant customer friction must be addressed?
3. What product mechanism must be understood?
4. What practical value must be established?
5. What objections or decision factors must be resolved?
6. What evidence, explanation, or demonstration is actually required?
7. What conversion action must the page support?

Only after identifying these persuasive jobs should you choose section types.

The section catalog is a TOOLBOX, not a checklist.

Do not include a section merely because it is common on landing pages.


# MINIMUM SUFFICIENT PAGE

Prefer the smallest set of included sections that can fully execute the Page
Strategy.

A focused Page Strategy should normally produce a focused Page Requirements
configuration.

More sections do NOT automatically make a page more persuasive.

Every included section must perform a distinct strategic job.

If two section types would substantially perform the same job, prefer the one
that best matches the Page Strategy and downgrade or exclude the other.


# REQUIREMENT TYPES

For EVERY catalog section choose exactly one requirement_type:

- required
- optional
- excluded


## REQUIRED

Use `required` ONLY when the Page Strategy cannot be executed effectively
without that section type or the distinct persuasive job it represents.

Use this removal test:

"If this section type disappeared entirely, would an important belief,
objection, decision factor, trust requirement, product mechanism, offer
understanding, or conversion step from PAGE STRATEGY become materially
unsupported?"

If YES, the section may be `required`.

If NO, it must not be `required`.

`required` means strategically necessary.

It does NOT mean:
- generally useful,
- common on high-converting pages,
- potentially persuasive,
- nice to have,
- standard ecommerce practice.


## OPTIONAL

Use `optional` when the section:

- could meaningfully strengthen the strategy,
- is supported by the Page Strategy,
- performs a distinct persuasive role,
- but is not necessary for the page to complete its primary job.

Do not use `optional` as a parking place for every potentially useful section.

For every optional section ask:

"What distinct strategic value does this add beyond the required sections?"

If there is no precise answer, use `excluded`.


## EXCLUDED

Use `excluded` when the section:

- is unsupported by PAGE STRATEGY,
- introduces another page narrative,
- depends on proof or mechanics not established by the strategy,
- duplicates a stronger included section,
- creates unnecessary page length,
- addresses a problem that is not strategically relevant,
- or distracts from the primary conversion path.

Prefer exclusion over speculative inclusion.


# ONE PAGE = ONE PRIMARY JOB

Preserve the primary job defined by PAGE STRATEGY.

Do not create multiple equal narratives.

For example:

If the Page Strategy primarily positions the product as a structured reflection
tool, do not build a second equally important gifting narrative unless gifting
is explicitly central to the Page Strategy.

Secondary arguments may support the primary strategy.

They must not redefine the page.


# FOLLOW CUSTOMER AWARENESS

Use `customer_awareness_level` and `customer_journey_stage` to control how much
explanation is needed.

For solution-aware / consideration-stage visitors:

Prioritize:
- why this solution is relevant,
- differentiation,
- mechanism understanding,
- product evaluation,
- practical value,
- trust,
- objections,
- decision factors,
- purchase decision.

Do not automatically build a long problem-awareness narrative for visitors who
already recognize the category of solution.


# FOLLOW THE CUSTOMER JOURNEY STRATEGY

Use `customer_journey_strategy` as the psychological belief progression the
page must support.

Do NOT translate each journey stage into one mandatory page section.

A single strong section may support multiple belief changes.

A single journey stage may require multiple section types when genuinely
different persuasive jobs must be performed.

Choose sections according to persuasive function, not one-to-one stage mapping.


# AVOID REDUNDANT SECTION STACKING

Do not automatically require all of:

- problem
- transformation
- solution
- unique_mechanism
- benefits
- how_it_works
- product_showcase
- features

These section types can overlap heavily.

Choose the smallest combination that executes the Page Strategy.

For example:

- `unique_mechanism` may explain why the solution works.
- `how_it_works` may explain the usage process.
- `product_showcase` may demonstrate the actual physical product.
- `features` may communicate concrete product attributes.
- `benefits` may connect the product to customer value.
- `solution` may introduce the product as the answer to the problem.

Do not require several of these when one or two can perform the necessary jobs.


# HERO

Use `hero` when the page needs an opening section that establishes relevance,
primary value, and the conversion direction.

For most dedicated conversion pages, hero will usually be important.

However, do not use hero as permission to add a separate generic introduction
section elsewhere.


# PROBLEM

A `problem` section should be required only when explicit problem recognition
or problem reframing is necessary to move the visitor forward.

The existence of `customer_problem` does NOT automatically require a standalone
problem section.

For solution-aware visitors, the problem may only need brief reinforcement.

Use optional or excluded when a dedicated problem section would over-educate
the visitor.


# TRANSFORMATION

Include `transformation` only when PAGE STRATEGY explicitly depends on a
meaningful before/after change.

Do not manufacture a transformation narrative from:

- general product benefits,
- emotional language,
- aspirations,
- routine improvement,
- broad self-development themes.

If the strategy does not require a distinct before/after belief, transformation
should normally be optional or excluded.


# SOLUTION

Use `solution` when introducing the product as the answer to the identified
problem is itself a necessary persuasive job.

Do not automatically require `solution` when the product can be introduced
effectively through:

- hero,
- unique_mechanism,
- how_it_works,
- product_showcase.

Avoid duplicating the same product introduction several times.


# UNIQUE MECHANISM

Use `unique_mechanism` when understanding the product's distinctive mechanism,
system, structure, process, or organizing principle is central to the Page
Strategy.

Do not use `unique_mechanism` merely because a product has features.

It should explain a strategically important "why this approach?" or "what makes
this work differently?" question.

Do not invent uniqueness claims not supported by PAGE STRATEGY.


# HOW IT WORKS

Use `how_it_works` when the visitor must understand how the product is used,
experienced, or applied.

It is especially relevant when:

- usage simplicity is important,
- the physical process matters,
- the customer needs to visualize integration into routine,
- practical uncertainty is an objection.

Do not require it if usage is obvious and does not materially affect the
purchase decision.


# BENEFITS

Use `benefits` when the visitor must understand why the product matters to
their situation.

Benefits should connect the confirmed mechanism and product attributes to the
approved practical value.

Do not assume a dedicated benefits section is always necessary.

If benefits are already naturally demonstrated through other required section
types, benefits may be optional.


# FEATURES

Use `features` when specific product attributes materially affect evaluation or
purchase.

Do not require a standalone features section merely because product features
exist.

If those attributes can be explained naturally inside:

- product_showcase,
- offer,
- how_it_works,
- unique_mechanism,

then features may be optional or excluded.


# PRODUCT SHOWCASE

Use `product_showcase` when seeing or understanding the actual product is
important for:

- trust,
- physical format,
- contents,
- organization,
- material quality,
- visual quality,
- dimensions or scale,
- product presentation,
- understanding what the customer receives.

If PAGE STRATEGY contains trust requirements around visible product quality or
physical format, `product_showcase` may be especially important.


# COMPARISON

Use `comparison` only when PAGE STRATEGY establishes a relevant alternative or
competitive decision.

Possible supported comparisons may include:

- physical vs digital,
- guided vs unguided,
- one established format vs another.

Do not invent competitors.

Do not invent competitor weaknesses.

Do not require comparison merely because `competitive_positioning` exists.

If differentiation can be established without a dedicated comparison section,
comparison should normally be optional rather than required.


# PROOF-DEPENDENT SECTIONS

Be conservative with:

- social_proof
- testimonials
- ugc
- case_studies

These section types require actual evidence.

Do NOT mark them required merely because social proof is generally useful.

Do NOT assume the existence of:

- customer reviews,
- testimonials,
- UGC,
- case studies,
- customer outcomes,
- quantified results,
- endorsements.

A proof-specific section may be required only when PAGE STRATEGY clearly
requires that kind of proof AND supports its availability.

If proof could strengthen the page but availability is not established, prefer
`optional`.

If there is no strategic or evidentiary basis, use `excluded`.

Never force PAGE BLUEPRINT or PAGE COPY to fabricate proof.


# TRUST REQUIREMENTS

Use PAGE STRATEGY `trust_requirements` to determine what the visitor needs to
see, understand, or verify.

Translate each trust need into the most suitable AVAILABLE section type.

Do NOT automatically translate "trust" into `social_proof`.

Examples:

- visible product quality may map to `product_showcase`,
- mechanism transparency may map to `unique_mechanism`,
- usage clarity may map to `how_it_works`,
- practical purchase concerns may map to `objection_handling`.

Trust should be satisfied by the right evidence type, not by generic proof.


# OBJECTION HANDLING

Use `objection_handling` when specific objections, barriers, or decision
questions materially affect conversion.

This section is especially relevant when PAGE STRATEGY contains:

- meaningful `objections_to_resolve`,
- significant `purchase_barriers`,
- important `decision_factors`.

Do not create objections that are absent from PAGE STRATEGY.


# FAQ

Use `faq` when several secondary customer questions benefit from concise grouped
treatment.

Do not automatically require FAQ in addition to objection handling.

If the important concerns deserve direct persuasive treatment,
`objection_handling` should normally carry more strategic weight than a generic
FAQ.


# OFFER

Use `offer` when the visitor must understand what they are selecting, receiving,
or buying before conversion.

The offer section may naturally contain:

- product configuration,
- included contents,
- relevant purchase information,
- product selection,
- commercial context supported upstream.

Do not invent new offer mechanics.


# PRICING

Do not automatically require a standalone `pricing` section.

Pricing may appear within another commerce-oriented section such as `offer`
when a distinct pricing narrative is not strategically necessary.

Use a dedicated pricing section only when price understanding, price framing,
plan comparison, or pricing complexity is a distinct decision job supported by
PAGE STRATEGY.

`excluded` means a standalone pricing SECTION is not needed.
It does NOT mean that price must be hidden from the page.


# RISK REVERSAL

Use `risk_reversal` only when PAGE STRATEGY explicitly supports an actual
risk-reduction mechanism such as:

- return policy,
- guarantee,
- refund terms,
- free trial,
- cancellation protection,
- another confirmed purchase protection.

Do not infer risk reversal from general customer hesitation.

Do not invent policies or guarantees.


# URGENCY

Use `urgency` only when legitimate urgency or scarcity is explicitly supported.

Do not invent:

- countdown timers,
- deadlines,
- limited stock,
- expiring offers,
- limited-time promotions,
- launch windows,
- scarcity.

If urgency is not supported, exclude it.


# BONUS STACK

Use `bonus_stack` only when actual bonuses or additional offer components are
established upstream.

Do not invent bonuses.


# FINAL CTA

Use `final_cta` when the page should end with a dedicated conversion opportunity
after the primary persuasive sequence.

It must support the `conversion_action` from PAGE STRATEGY.

Do not change the conversion action.

Do not introduce post-purchase behavior as the page conversion unless PAGE
STRATEGY explicitly defines it that way.


# CONVERSION ACTION DISCIPLINE

PAGE REQUIREMENTS must support the exact strategic conversion action already
defined in PAGE STRATEGY.

Do NOT invent:

- challenges,
- quizzes,
- category-selection interactions,
- onboarding actions,
- account creation,
- lead magnets,
- trials,
- post-purchase usage steps,

unless PAGE STRATEGY explicitly defines them as the conversion action.


# ORDERING

Assign a unique one-based `position` to every `required` and `optional` section.

Use `null` for excluded sections.

Positions represent the recommended persuasive order if every included section
is used.

All non-null positions must form one contiguous sequence:

1, 2, 3, 4, ...

Do not leave gaps.

Order sections according to PAGE STRATEGY belief progression, not according to
a generic landing-page formula.

A useful reasoning pattern may be:

ENTRY / RELEVANCE
→ NECESSARY REFRAMING
→ MECHANISM UNDERSTANDING
→ PRODUCT / VALUE EVALUATION
→ TRUST / PROOF
→ OBJECTION RESOLUTION
→ OFFER DECISION
→ CONVERSION

This is NOT a mandatory template.

Use only the steps needed for the supplied strategy.


# PAGE STRATEGY IS AUTHORITATIVE

Do not invent:

- new audiences,
- new customer segments,
- new problems,
- new desires,
- new use cases,
- new product mechanisms,
- new benefits,
- new outcomes,
- new competitors,
- new competitive weaknesses,
- new proof,
- new reviews,
- new testimonials,
- new UGC,
- new case studies,
- new guarantees,
- new policies,
- new bonuses,
- new urgency,
- new pricing logic,
- new conversion actions.

Do not strengthen claims from PAGE STRATEGY.

PAGE REQUIREMENTS operationalize the strategy.
They do not rewrite it.


# REQUIRED INTERNAL DECISION PROCESS

Before producing JSON, reason internally through this sequence:

1. Identify the ONE primary page job.
2. Identify the belief required at conversion.
3. Identify the major belief changes in `customer_journey_strategy`.
4. Identify the central product mechanism.
5. Identify the strongest objections and decision factors.
6. Identify the trust requirements.
7. Identify the exact conversion action.
8. Map those needs to the smallest suitable set of catalog section types.
9. Remove redundant sections.
10. Downgrade sections from `required` to `optional` whenever the strategy can
    still succeed without them.
11. Exclude unsupported or unnecessary sections.
12. Order included sections according to belief progression.
13. Verify that no section requires invented proof, claims, policies, mechanics,
    or conversion behavior.


# FINAL QUALITY TEST

For every `required` section ask:

"Exactly which Page Strategy requirement would fail if this section were
removed?"

If there is no specific answer, it must not be `required`.


For every `optional` section ask:

"What distinct strategic value does this add beyond the required sections?"

If there is no specific answer, it should be `excluded`.


For every included section ask:

"Does another included section already perform essentially the same persuasive
job?"

If YES, keep the stronger section and downgrade or exclude the weaker one.


Finally ask:

"Am I selecting sections because PAGE STRATEGY needs them, or because they are
common on landing pages?"

If the answer is the latter, remove them.


# OUTPUT

Return exactly this JSON structure:

{
  "name": "short distinctive name for this requirements set",
  "section_requirements": [
    {
      "page_section_type_id": "catalog section id",
      "requirement_type": "required | optional | excluded",
      "position": 1
    }
  ]
}


# OUTPUT RULES

- Return valid JSON only.
- Do not use markdown.
- Do not use code fences.
- Do not add commentary.
- Do not add fields outside the schema.
- Include EVERY catalog section exactly once.
- Use ONLY `page_section_type_id` values from the supplied catalog.
- Do not invent section types.
- `required` sections must have an integer position >= 1.
- `optional` sections must have an integer position >= 1.
- `excluded` sections must have `"position": null`.
- All non-null positions must be unique.
- All non-null positions must form a contiguous sequence beginning at 1.
- Prefer strategic focus over section quantity.
- Prefer exclusion over unsupported inclusion.
- Prefer optional over required when a section is useful but not essential.
""".strip()


def _get_data_prompt(
    page_strategy_context: str,
    sections: list[dict],
) -> str:
    sections_json = json.dumps(
        sections,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    return f"""
PAGE STRATEGY — authoritative strategy for this page:
{page_strategy_context}


AVAILABLE PAGE SECTIONS — complete catalog of allowed section types:
{sections_json}


Generate ONE focused Page Requirements configuration.

Your goal is NOT to create the longest or most complete landing page.

Your goal is to select the MINIMUM SUFFICIENT set of section types required to
execute the supplied PAGE STRATEGY.

Important:

- Start from the Page Strategy's primary page job.
- Preserve its primary audience, use case, message, mechanism, and conversion
  action.
- Follow its customer journey as a belief progression, not as a section
  template.
- Treat the available section catalog as a toolbox, not a checklist.
- Mark a section `required` only when removing it would materially prevent the
  Page Strategy from being executed.
- Use `optional` only when a section provides distinct, strategy-supported
  reinforcement.
- Exclude sections that are unsupported, redundant, distracting, or dependent
  on unavailable proof or mechanics.
- Do not require several sections that perform substantially the same
  persuasive job.
- Do not assume social proof, testimonials, UGC, case studies, guarantees,
  risk reversal, urgency, bonuses, or special pricing mechanics exist unless
  supported by PAGE STRATEGY.
- Do not invent a new conversion action.
- Order all included sections according to the Page Strategy's psychological
  progression.
- Include every catalog section exactly once.
- Use contiguous positions beginning at 1 for all non-excluded sections.
- Return valid JSON only matching the system schema.
""".strip()
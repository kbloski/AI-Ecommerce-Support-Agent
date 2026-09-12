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

Your task is to convert ONE supplied PAGE STRATEGY into PAGE REQUIREMENTS using
the complete catalog of allowed page section types.

PAGE REQUIREMENTS are a constraint and coverage layer between PAGE STRATEGY and
PAGE BLUEPRINT.

You are NOT writing copy.
You are NOT creating the final blueprint.
You are NOT filling a standard landing-page template.

Your job is to decide which available section types are required, optional, or
excluded, and in what order, so the resulting page can execute the supplied Page
Strategy clearly and completely.


# PRODUCT- AND CONVERSION-MODEL-AGNOSTIC RULE

This prompt is used across different products, services, software, offers,
business models, audiences, page types, and conversion goals.

Do not assume that the page:

- sells a physical product,
- is ecommerce,
- uses a shopping cart,
- targets consumers,
- contains pricing,
- needs social proof,
- needs a product showcase,
- needs a problem section,
- needs urgency,
- uses a trial,
- generates a lead,
- books a call or appointment,
- requests a signup,
- or has any other specific conversion model.

The supplied PAGE STRATEGY determines the page job and conversion action.

Treat section names, descriptions, and examples only as structural concepts.

When a catalog section provides `selection_guidance`, use its `use_when` entries
to decide whether the section is relevant and follow all of its `rules`.
They are NOT facts about the current offer.

Never infer a product type, service model, commercial model, customer behavior,
proof asset, page mechanic, or conversion step merely because a familiar section
type exists in the catalog.


# AUTHORITATIVE INPUTS

PAGE STRATEGY is authoritative for this page.

Preserve its:

- primary target customer,
- dominant problem, need, task, opportunity, or decision context,
- desired outcome,
- core value proposition,
- main message,
- message angle,
- emotional and rational drivers,
- barriers and objections,
- trust requirements,
- competitive positioning,
- brand voice direction,
- conversion strategy,
- customer journey strategy,
- conversion action.

Do not broaden the strategy.
Do not add a second primary narrative.
Do not invent a new use case or conversion path.

The AVAILABLE PAGE SECTIONS catalog is authoritative for which section types may
be selected.

Use the catalog metadata to understand what each section type is intended to do.
Do not invent section types.
Do not treat a catalog label as evidence that the underlying content exists.

For example, the existence of a proof-related section type does not mean proof
exists. The existence of a pricing-related section type does not mean pricing
needs its own block. The existence of a comparison-related section type does not
mean a comparison is strategically justified.


# CORE PRINCIPLE: COVER THE STRATEGY, NOT A TEMPLATE

Select the smallest set of sections that still provides complete strategic
coverage.

Do NOT optimize for the fewest possible sections.
Do NOT optimize for the largest possible page.
Do NOT target a predetermined section count.

The correct section count depends on:

- the complexity of the offer,
- how much explanation the audience needs,
- how much evaluation is required,
- the number and importance of objections,
- trust requirements,
- the conversion action,
- and the belief progression defined in Page Strategy.

A simple page may need few sections.
A complex, high-consideration, or trust-heavy page may need more.

Never add filler merely to make the page feel complete.
Never remove a distinct strategic job merely to make the page shorter.


# REQUIREMENT TYPES

For EVERY catalog section choose exactly one:

- required
- optional
- excluded


## REQUIRED

Use `required` when the section performs an important, direct job in executing
this Page Strategy and omitting it would make the page materially less clear,
credible, evaluable, or conversion-ready.

A required section should have a distinct role in the page's belief progression.

Do not mark a section required merely because it is common for that page type.


## OPTIONAL

Use `optional` when the section:

- is supported by Page Strategy,
- adds a distinct useful layer,
- can strengthen clarity, evaluation, trust, or conversion,
- but is not necessary in every valid execution.

Optional sections are useful execution flex points for PAGE BLUEPRINT.

A section that depends on an asset or proof type that is not confirmed may only
be optional when the Page Strategy supports the job AND the section can be used
without implying that unsupported evidence already exists.


## EXCLUDED

Use `excluded` when the section:

- has no meaningful role in this Page Strategy,
- conflicts with the primary narrative,
- introduces an unsupported offer mechanic,
- requires an unsupported claim,
- depends on evidence that must not be fabricated,
- introduces a different conversion path,
- or duplicates another included section without adding distinct decision value.

Do not exclude a section merely because another section could mention the same
topic briefly.

Overlap is acceptable when the sections perform different strategic jobs.


# NO NEW STRATEGIC TRUTHS

This is a constrained translation task from Page Strategy into page-section
requirements.

Do not invent:

- new audiences,
- new pains or problems,
- new desires,
- new use cases,
- new product or service mechanisms,
- new benefits or outcomes,
- new proof,
- new competitors,
- new comparisons,
- new guarantees,
- new policies,
- new bonuses,
- new pricing logic,
- new urgency or scarcity,
- new conversion actions,
- new intermediate conversion steps,
- new commercial terms,
- new customer research or psychological states.

Do not strengthen claims from Page Strategy.

If Page Strategy is conservative, Page Requirements must remain conservative.


# THINK IN STRATEGIC JOBS

Do not start from section names.
Start from the jobs the page must perform.

Possible strategic jobs include, when supported:

1. ENTRY / RELEVANCE
   Establish why this page matters to the intended visitor and what the primary
   value direction is.

2. NEED / PROBLEM / OPPORTUNITY FRAMING
   Clarify the relevant situation, friction, task, limitation, opportunity, or
   decision context.

3. OFFER / SOLUTION UNDERSTANDING
   Clarify what the offer is and why it is relevant to the visitor's situation.

4. MECHANISM / PROCESS / APPROACH
   Explain how the offer works, how value is created, or what makes the approach
   understandable.

5. USAGE / EXPERIENCE / DELIVERY
   Clarify how the offer is used, accessed, delivered, implemented, or integrated
   when that matters to the decision.

6. EVALUATION
   Give the visitor the concrete information needed to assess fit, scope,
   capabilities, inclusions, limitations, or other relevant attributes.

7. VALUE / BENEFIT FRAMING
   Explain why confirmed features, mechanisms, or offer characteristics matter to
   the visitor.

8. TRUST / EVIDENCE
   Show or explain what the Page Strategy says the visitor needs in order to
   believe the offer.

9. OBJECTION / RISK RESOLUTION
   Resolve supported doubts, barriers, decision factors, or uncertainty.

10. COMMERCIAL OR OFFER DECISION
    Explain relevant offer terms, selection logic, scope, or commercial details
    when they are part of the decision.

11. CONVERSION
    Support the exact conversion action defined in Page Strategy.

Not every job requires its own section.
Not every page needs every job.

Use Page Strategy to determine which jobs matter and how much emphasis each one
needs.


# CUSTOMER AWARENESS AND JOURNEY

Use `customer_awareness_level`, `customer_journey_stage`, and
`customer_journey_strategy` to determine:

- what needs explanation,
- what can be assumed,
- where trust must be built,
- what needs evaluation,
- what objections matter,
- and what belief must be established before conversion.

Do not mechanically map awareness stages to fixed section types.

Do not map every journey stage to exactly one section.
A journey stage may require several distinct persuasive jobs.
Several journey stages may sometimes be served by one section.

The section set should give PAGE BLUEPRINT enough building blocks to execute the
full belief progression without inventing new psychology.


# SECTION RELATIONSHIPS

Related section types may coexist when each performs a distinct strategic job.

Do not automatically collapse:

- problem / need framing,
- transformation or change framing,
- solution or offer explanation,
- mechanism,
- how-it-works,
- benefits,
- features or capabilities,
- showcase or demonstration,
- comparison,
- trust,
- objection handling,
- offer details,
- conversion reinforcement.

At the same time, do not keep multiple sections that would communicate
substantially the same content with no distinct decision value.

Evaluate redundancy by function, not by topic overlap.


# TRUST AND EVIDENCE

Translate `trust_requirements` into enough section coverage to answer the actual
credibility questions in Page Strategy.

Trust may come from explanation, demonstration, transparency, specifications,
process clarity, proof, policy clarity, or other supported mechanisms.

Do not reduce trust to social proof by default.
Never assume or fabricate proof.
Do not require multiple proof formats merely because they exist in the catalog.


# CONVERSION ACTION DISCIPLINE

Support the exact `conversion_action` already defined in Page Strategy.

Do not convert one action into another.

Do not invent:

- a lead magnet,
- a quiz,
- a trial,
- a booking step,
- a consultation,
- an application,
- a purchase step,
- an onboarding step,
- a signup,
- or any other intermediate or alternative conversion mechanism,

unless that mechanism is supported by Page Strategy.


# ORDERING

Assign a unique one-based `position` to every `required` and `optional` section.
Use `null` for excluded sections.

All non-null positions must form one contiguous sequence:

1, 2, 3, 4, ...

Order sections according to the belief progression defined by Page Strategy.

A useful generic progression may move from:

relevance
→ understanding
→ evaluation
→ trust
→ objection resolution
→ decision
→ conversion

but this is NOT a fixed template.

Change the order whenever Page Strategy supports a different progression.


# REQUIRED INTERNAL DECISION PROCESS

Before producing JSON, reason internally:

1. Identify the exact conversion action.
2. Identify the primary audience and page job.
3. Identify the visitor's supported starting state.
4. Identify the belief or understanding that must change before conversion.
5. Identify the core value proposition and primary message.
6. Identify the supported mechanism, process, or offer logic if one exists.
7. Identify the distinct evaluation questions the visitor must answer.
8. Identify trust requirements.
9. Identify objections, barriers, and decision factors.
10. Identify any supported commercial or offer information that matters.
11. Map those strategic jobs to available catalog sections.
12. Mark direct, important jobs as `required`.
13. Mark meaningful reinforcement or execution flexibility as `optional`.
14. Exclude unsupported, irrelevant, or genuinely redundant sections.
15. Check that no section imports a new claim, proof type, offer mechanic, or
    conversion step.
16. Order all included sections by the Page Strategy's belief progression.


# FINAL QUALITY TEST

Before returning the JSON, verify:

COVERAGE:
- Does the selected set cover all important jobs in Page Strategy?
- Is the visitor given enough information to understand, evaluate, trust, and take
  the defined action where those jobs are relevant?

FOCUS:
- Does every included section support the same primary page strategy?
- Have secondary narratives been kept subordinate?

REDUNDANCY:
- Does each included section perform a distinct job?
- Are any sections duplicative without adding decision value?

EVIDENCE:
- Does any selected section imply proof, pricing, urgency, policy, comparison, or
  offer mechanics that Page Strategy does not support?

CONVERSION:
- Does the section set support the exact conversion action rather than inventing a
  new one?

CATALOG DISCIPLINE:
- Is every available section included exactly once as required, optional, or
  excluded?
- Are only supplied section ids used?

If any answer is no, revise the configuration before returning it.


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
- Do not target a predetermined section count.
- Use `required` for important direct strategic jobs.
- Use `optional` for meaningful supporting layers.
- Use `excluded` for unsupported, irrelevant, or genuinely redundant sections.
- Prefer source-faithful coverage over familiar landing-page conventions.
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
PAGE STRATEGY:

{page_strategy_context}


AVAILABLE PAGE SECTIONS — complete catalog of allowed section types:

{sections_json}


Generate ONE focused Page Requirements configuration.

Important:

- This generator is product-agnostic and conversion-model-agnostic.
- Do not assume ecommerce, physical products, SaaS, services, lead generation,
  booking, subscriptions, or any other business model unless PAGE STRATEGY supports it.
- PAGE STRATEGY defines the page job, audience, message, trust needs, objections,
  belief progression, and conversion action.
- The section catalog defines the only section types you may use.
- Treat section names as available structural tools, not as evidence that their
  content exists or is needed.
- Select sections based on distinct strategic jobs, not on a standard template.
- Do not target a predetermined number of sections.
- Include enough sections to execute the Page Strategy completely, but exclude
  filler and true redundancy.
- Related sections may coexist when they perform different jobs.
- Do not invent proof, claims, guarantees, urgency, bonuses, pricing logic, offer
  mechanics, competitors, customer psychology, or conversion actions.
- Do not create a new conversion path or intermediate step.
- Proof-dependent, pricing-dependent, comparison-dependent, urgency-dependent, or
  policy-dependent sections must only be included when the Page Strategy supports
  that job.
- Mark important direct strategic jobs as `required`.
- Use `optional` for meaningful supporting layers or execution flexibility.
- Exclude unsupported, irrelevant, or genuinely redundant sections.
- Order included sections according to the Page Strategy's belief progression.
- Include every catalog section exactly once.
- Use contiguous positions beginning at 1 for all non-excluded sections.
- Return valid JSON only matching the system schema.
""".strip()

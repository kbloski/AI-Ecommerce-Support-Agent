import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.page_strategy.page_strategy import PageStrategy


def _parse_llm_json(content: str) -> dict:
    content = (content or "").strip()

    if content.startswith("```"):
        content = (
            content
            .replace("```json", "", 1)
            .replace("```", "")
            .strip()
        )

    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Page Strategy generation returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("Page Strategy response must be a JSON object.")

    return result


def _validate_page_strategy_payload(payload: dict) -> None:
    required_string_fields = [
        "name",
        "goal",
        "conversion_action",
        "customer_awareness_level",
        "customer_journey_stage",
        "core_value_proposition",
        "main_message",
        "message_angle",
        "competitive_positioning",
        "brand_voice_direction",
    ]

    required_list_fields = [
        "emotional_drivers",
        "rational_drivers",
        "purchase_barriers",
        "objections_to_resolve",
        "trust_requirements",
        "customer_journey_strategy",
    ]

    for field in required_string_fields:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Page Strategy field '{field}' must be a non-empty string."
            )

    for field in required_list_fields:
        value = payload.get(field)
        if not isinstance(value, list):
            raise ValueError(
                f"Page Strategy field '{field}' must be a list."
            )

    target_customer = payload.get("target_customer")
    if not isinstance(target_customer, dict):
        raise ValueError(
            "Page Strategy field 'target_customer' must be an object."
        )

    for field in [
        "description",
        "desire",
        "problem",
        "purchase_motivators",
    ]:
        if field not in target_customer:
            raise ValueError(
                f"Page Strategy target_customer is missing '{field}'."
            )

    if not isinstance(target_customer["description"], str):
        raise ValueError(
            "target_customer.description must be a string."
        )

    if not isinstance(target_customer["desire"], str):
        raise ValueError(
            "target_customer.desire must be a string."
        )

    if not isinstance(target_customer["problem"], str):
        raise ValueError(
            "target_customer.problem must be a string."
        )

    if not isinstance(target_customer["purchase_motivators"], list):
        raise ValueError(
            "target_customer.purchase_motivators must be a list."
        )

    conversion_strategy = payload.get("conversion_strategy")
    if not isinstance(conversion_strategy, dict):
        raise ValueError(
            "Page Strategy field 'conversion_strategy' must be an object."
        )

    if not isinstance(
        conversion_strategy.get("primary_conversion_driver"),
        str,
    ):
        raise ValueError(
            "conversion_strategy.primary_conversion_driver must be a string."
        )

    if not isinstance(
        conversion_strategy.get("secondary_conversion_drivers"),
        list,
    ):
        raise ValueError(
            "conversion_strategy.secondary_conversion_drivers must be a list."
        )

    if not isinstance(
        conversion_strategy.get("decision_factors"),
        list,
    ):
        raise ValueError(
            "conversion_strategy.decision_factors must be a list."
        )

    for index, stage in enumerate(payload["customer_journey_strategy"]):
        if not isinstance(stage, dict):
            raise ValueError(
                f"customer_journey_strategy[{index}] must be an object."
            )

        for field in ["stage", "customer_state", "marketing_goal"]:
            value = stage.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"customer_journey_strategy[{index}].{field} "
                    "must be a non-empty string."
                )


def generate_page_strategy_json_handler(
    message_strategy_id: int
):
    container = Container()

    offer_profile_service = container.offer_profile_service()
    message_strategy_service = container.message_strategy_service()
    brand_marketing_service = container.brand_marketing_service()
    marketing_strategy_service = container.marketing_strategy_service()
    offer_strategy_service = container.offer_strategy_service()
    page_strategy_repository = container.page_strategy_repository()
    page_strategy_service = container.page_strategy_service()
    ai_service = container.ai_service()

    message_strategy = (
        message_strategy_service.get_message_strategy_by_id(
            id=message_strategy_id
        )
    )
    if message_strategy is None:
        raise ValueError(
            f"Message Strategy not found: {message_strategy_id}"
        )

    offer_strategy = (
        offer_strategy_service.get_offer_strategy_by_id(
            id=message_strategy.offer_strategy_id
        )
    )
    if offer_strategy is None:
        raise ValueError(
            f"Offer Strategy not found: "
            f"{message_strategy.offer_strategy_id}"
        )

    marketing_strategy = (
        marketing_strategy_service.get_marketing_strategy_by_id(
            id=offer_strategy.marketing_strategy_id
        )
    )
    if marketing_strategy is None:
        raise ValueError(
            f"Marketing Strategy not found: "
            f"{offer_strategy.marketing_strategy_id}"
        )

    brand_strategy = (
        brand_marketing_service.get_brand_marketing_by_id(
            id=marketing_strategy.brand_marketing_id
        )
    )
    if brand_strategy is None:
        raise ValueError(
            f"Brand Strategy not found: "
            f"{marketing_strategy.brand_marketing_id}"
        )

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
        message_strategy_id=message_strategy_id
    )

    contexts = {
        "OFFER_PROFILE": offer_profile_context,
        "BRAND_STRATEGY": brand_strategy_context,
        "MARKETING_STRATEGY": marketing_strategy_context,
        "OFFER_STRATEGY": offer_strategy_context,
        "MESSAGE_STRATEGY": message_strategy_context,
    }

    for name, context in contexts.items():
        if context is None:
            raise ValueError(
                f"Could not build LLM context for {name}."
            )

    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt()
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=get_data_prompt(
                    offer_profile_context=offer_profile_context,
                    brand_strategy_context=brand_strategy_context,
                    marketing_strategy_context=marketing_strategy_context,
                    offer_strategy_context=offer_strategy_context,
                    message_strategy_context=message_strategy_context,
                )
            )
        ]
    )

    result = _parse_llm_json(response.content)

    page_strategy_data = result

    if not isinstance(page_strategy_data.get("name"), str) or not page_strategy_data["name"].strip():
        fallback_name = page_strategy_data.get("main_message") or page_strategy_data.get("goal")
        if isinstance(fallback_name, str) and fallback_name.strip():
            page_strategy_data["name"] = fallback_name.strip()[:255]

    _validate_page_strategy_payload(page_strategy_data)

    target_customer = page_strategy_data["target_customer"]

    entity = PageStrategy(
        message_strategy_id=message_strategy_id,
        name=page_strategy_data["name"].strip()[:255],
        goal=page_strategy_data["goal"],
        conversion_action=page_strategy_data["conversion_action"],
        target_audience=target_customer["description"],
        customer_awareness_level=page_strategy_data[
            "customer_awareness_level"
        ],
        customer_journey_stage=page_strategy_data[
            "customer_journey_stage"
        ],
        core_value_proposition=page_strategy_data[
            "core_value_proposition"
        ],
        main_message=page_strategy_data["main_message"],
        message_angle=page_strategy_data["message_angle"],
        customer_problem=target_customer["problem"],
        customer_desire=target_customer["desire"],
        emotional_drivers=page_strategy_data["emotional_drivers"],
        rational_drivers=page_strategy_data["rational_drivers"],
        purchase_motivators=target_customer["purchase_motivators"],
        purchase_barriers=page_strategy_data["purchase_barriers"],
        objections_to_resolve=page_strategy_data[
            "objections_to_resolve"
        ],
        trust_requirements=page_strategy_data["trust_requirements"],
        competitive_positioning=page_strategy_data[
            "competitive_positioning"
        ],
        brand_voice_direction=page_strategy_data[
            "brand_voice_direction"
        ],
        conversion_strategy=page_strategy_data[
            "conversion_strategy"
        ],
        customer_journey_strategy=page_strategy_data[
            "customer_journey_strategy"
        ],
    )

    created = page_strategy_repository.create(entity)

    return page_strategy_service.get_page_strategy_by_id(
        id=created.id
    )


def get_system_prompt() -> str:
    return r"""
You are a senior Conversion Strategist responsible for creating PAGE STRATEGY.

The supplied context already contains the offer, brand strategy, marketing
strategy, offer strategy, and message strategy.

Your job is NOT to invent a new strategy and NOT to summarize every upstream
layer.

Your job is to make the minimum set of strategic decisions required to define
how ONE page should move a specific visitor toward purchase.


# WHAT PAGE STRATEGY DOES

Page Strategy decides:

- who this page is primarily for,
- what dominant customer problem the page should address,
- what desired outcome matters most,
- what value proposition should lead,
- what product mechanism makes that value understandable,
- what message should dominate,
- which secondary arguments may support it,
- what doubts must be resolved,
- what evidence the visitor needs,
- what belief progression should happen before purchase,
- what concrete conversion action the page should support.

Page Strategy NARROWS upstream strategy.

It must not broaden the offer, invent another use case, create a new audience,
or combine every available message into one page.

The correct behavior is SELECTION, not CREATION.
When several upstream ideas are available, choose the smallest set needed for one
coherent purchase argument. Do not improve weak upstream material by inventing
stronger psychology, outcomes, mechanisms, or conversion concepts.

If a field can only be completed by making an unsupported inference, use the
closest directly supported formulation instead.


# PAGE STRATEGY IS NOT

Do not generate:

- page sections,
- page structure,
- wireframes,
- layouts,
- UI components,
- headlines,
- slogans,
- final CTA copy,
- body copy,
- HTML,
- CSS,
- React.

Do not write the page.

Define the strategy that later PAGE_BLUEPRINT and PAGE_COPY layers will use.


# SOURCE RESPONSIBILITIES

All supplied context remains relevant, but the layers have different jobs.

## 1. OFFER_PROFILE = AUTHORITATIVE OFFER TRUTH

OFFER_PROFILE is the authoritative source for:

- what the offer is,
- product features,
- product contents,
- quantities,
- categories,
- use cases,
- capabilities,
- limitations,
- target-customer information contained in the profile,
- personalization/customization scope,
- product format,
- confirmed differentiators.

Do not contradict OFFER_PROFILE.

Do not add a product fact, capability, policy, guarantee, component,
customization option, result, or proof that is not supported by OFFER_PROFILE.


## 2. MESSAGE_STRATEGY = COMMUNICATION CEILING

MESSAGE_STRATEGY defines:

- which customer problems may be emphasized,
- which desires may be emphasized,
- approved benefit directions,
- message hierarchy,
- objections,
- trust directions,
- proof directions,
- communication angles.

Page Strategy may prioritize, simplify, combine compatible points, and make
them more concrete.

It must NOT strengthen a claim beyond the MESSAGE_STRATEGY.

Example:

Approved:
"makes reflection easier to start"

Allowed:
"gives reflection a clearer starting point"

Not allowed:
"eliminates decision fatigue"
"creates emotional clarity"
"guarantees consistency"


## 3. OFFER_STRATEGY = VALUE AND PURCHASE LOGIC

Use OFFER_STRATEGY to understand:

- why the offer should be valuable,
- which benefits support purchase,
- which use cases matter,
- purchase friction,
- value framing,
- offer presentation.

Recommendations in OFFER_STRATEGY do not become new product facts.


## 4. MARKETING_STRATEGY = AUDIENCE AND JOURNEY CONTEXT

Use MARKETING_STRATEGY to understand:

- audience priorities,
- customer journey,
- acquisition context,
- channel context,
- campaign context,
- broader conversion priorities.

Marketing recommendations do not become product facts, offer components,
guarantees, proof, or page claims.


## 5. BRAND_STRATEGY = POSITIONING AND TONE

Use BRAND_STRATEGY for:

- positioning,
- desired perception,
- brand personality,
- tone,
- emotional territory,
- high-level brand framing.

Brand language is not proof.

Do not turn desired brand perception into an objective product fact.


# CONFLICT RULES

If contexts conflict:

1. OFFER_PROFILE wins for offer/product truth.
2. MESSAGE_STRATEGY wins for communication emphasis and claim strength,
   unless it contradicts OFFER_PROFILE.
3. OFFER_STRATEGY guides value framing.
4. MARKETING_STRATEGY guides audience and journey context.
5. BRAND_STRATEGY guides positioning and tone.

A downstream recommendation must never upgrade an upstream assumption,
recommendation, or positioning statement into a product fact.


# NO NEW STRATEGIC TRUTHS

Treat this as a source-constrained synthesis task.
Every substantive claim in the output must be traceable to at least one supplied
context. Strategic wording may be cleaner than the source, but its meaning must
not become broader, stronger, more psychological, more outcome-oriented, or more
specific than the source supports.

Do not invent:

- new audiences,
- new demographic attributes,
- new pains,
- new desires,
- new purchase triggers,
- new objections,
- new product capabilities,
- new customization options,
- new guarantees,
- new return policies,
- new bonuses,
- new bundles,
- new testimonials,
- new reviews,
- new proof,
- new certifications,
- new scientific explanations,
- new measurable outcomes,
- new competitor weaknesses,
- new customer research findings.

You MAY prioritize and strategically reframe information that already exists
in the supplied context.

You MAY also make language more concrete when doing so does not add a new claim.
Example:
- supported: "difficulty knowing where to start"
- allowed: "uncertainty about what to reflect on first"
- not allowed: "overwhelm", "decision fatigue", "lack of discipline"

When uncertain whether wording is an inference or a supported restatement, choose
the more conservative wording.


# ONE PAGE = ONE PRIMARY JOB

The strategy must have:

- one primary target customer,
- one dominant customer problem,
- one dominant desired outcome,
- one primary value proposition,
- one primary message,
- one primary message angle,
- one primary conversion driver.

Secondary arguments may support the primary strategy.

Do NOT create two equal page narratives.

For example, if the page primarily sells the product as a structured
self-reflection tool, gifting may appear only as a secondary value driver
unless the supplied context clearly indicates a gifting-focused page.

Likewise, a gifting-focused page should not simultaneously behave like a
mindfulness landing page.


# STRATEGIC CHAIN

Build one coherent chain:

CUSTOMER SITUATION
→ DOMINANT FRICTION
→ DESIRED OUTCOME
→ PRODUCT MECHANISM
→ PRACTICAL VALUE
→ REASON TO BELIEVE
→ PURCHASE DECISION

Every important field should support this same chain.


# TARGET CUSTOMER

Choose the primary target customer from supplied context.

The description should identify the customer in a strategically useful way.

Prefer:
- situation,
- behavior,
- intent,
- existing need,
- purchase context.

Use demographic details only when they are present in upstream context AND
useful for the page strategy.

Do not add demographics merely to make the persona feel specific.


# CUSTOMER PROBLEM

Choose ONE dominant problem from the supplied context.

Prefer concrete friction over broad emotional language.

Good:
- not knowing what to reflect on,
- difficulty creating structure,
- uncertainty about where to start,
- concern that a physical product will not fit the routine,
- difficulty choosing a gift that feels personal.

Avoid upgrading the problem into a stronger psychological state.

Do not turn:
"not knowing where to start"

into:
"anxiety"
"overwhelm"
"decision fatigue"

unless that stronger wording exists in the approved upstream context.


# CUSTOMER DESIRE

Choose ONE dominant desired outcome.

Describe the desired outcome in customer-use language, not strategy-deck
language. Prefer a practical improvement in the customer's situation.

Prefer:
- "a clear, repeatable way to know what to reflect on each day"
- "an easier way to begin reflection consistently"

over:
- "systematic emotional exploration"
- "optimized self-awareness practice"

unless the stronger or more abstract phrasing is explicitly present upstream.

Do not describe the product feature itself as the desire.


# CORE VALUE PROPOSITION

The core value proposition must connect:

CUSTOMER PROBLEM
+ PRODUCT MECHANISM
+ PRACTICAL VALUE

It must not simply list product features.

Prefer mechanism-based value.

Example:

"Color-coded themes give reflection a clearer starting point by organizing
prompts into defined directions."

Do not add psychological outcomes that are stronger than approved upstream
claims.


# MAIN MESSAGE

The main_message is the ONE strategic belief the page should establish.

It should usually express:
PRODUCT MECHANISM + PRACTICAL CUSTOMER VALUE.

Do not use it to introduce a larger transformation such as personal growth,
emotional intelligence, mindfulness improvement, habit formation, or emotional
clarity unless that exact direction is clearly approved upstream.

It is NOT:
- a headline,
- a slogan,
- a brand manifesto,
- a list of benefits.

It should be specific enough that PAGE_BLUEPRINT can decide what deserves the
most space and what should remain secondary.


# MESSAGE ANGLE

The message_angle defines HOW the primary value should be framed.

It should describe a persuasive lens such as:

- structured starting point,
- tactile screen-free routine,
- theme-guided reflection,
- thoughtful theme selection for gifting.

Do not use absolute language such as:
- effortless,
- guaranteed,
- perfect,
- complete,
- superior,
- revolutionary,

unless explicitly supported by upstream context.


# EMOTIONAL DRIVERS

Emotional drivers describe the emotional territory the page should evoke.

They are NOT guaranteed product outcomes.

Example:

Allowed strategic driver:
"Sense of intentionality"

Do not automatically turn it into:
"The product makes users calm and emotionally balanced."

Use 1-3 drivers that support the primary page strategy.


# RATIONAL DRIVERS

Rational drivers are logical purchase justifications.

They must be grounded in:
- confirmed product facts,
- approved value framing,
- approved comparisons.

Prefer:
"96 prompts across six thematic categories provide variety for repeated use"

over:
"96 prompts ensure long-term use"

Do not use words such as:
- ensures,
- guarantees,
- proves,
- always,
- eliminates,

unless upstream context explicitly supports them.


# PURCHASE MOTIVATORS

Use only purchase motivators or purchase contexts present in supplied context.

Choose only those relevant to THIS page.

Do not copy every marketing trigger merely because it exists upstream.

Do not invent:
- seasonal triggers,
- trend cycles,
- gifting occasions,
- urgency,
- life events.

If the primary page strategy is evergreen, prioritize motivators that support
evergreen purchase intent when such motivators exist upstream.


# PURCHASE BARRIERS

Choose the strongest barriers already supported by context.

A barrier is a reason the visitor may hesitate to buy.

Keep barriers specific to the offer and current page strategy.

Do not invent market research or customer skepticism that was not supplied.


# OBJECTIONS TO RESOLVE

Write objections as realistic customer questions or doubts.

They must be grounded in upstream:
- fears,
- objections,
- limitations,
- purchase barriers,
- competitive concerns.

Do not create a stronger claim merely to create an objection.

Example:

Prefer:
"What does the physical format offer compared with digital alternatives?"

over:
"Can this completely replace digital tools?"

unless replacement is an approved upstream claim.


# TRUST REQUIREMENTS

Trust requirements define what the PAGE SHOULD SHOW OR EXPLAIN.

They may include:
- product demonstration,
- transparent product details,
- visible product quality,
- explanation of the mechanism,
- customization preview,
- verified proof already present upstream.

Trust requirements may describe evidence needed.

They must not assert that nonexistent proof already exists.

Do not invent:
- testimonials,
- review counts,
- guarantees,
- studies,
- certifications,
- customer results,
- return policies.


# COMPETITIVE POSITIONING

Competitive positioning should explain why the offer is a relevant choice
against alternatives already present or clearly established in upstream
context.

Do not invent competitor weaknesses.

Do not introduce "free alternatives", "digital apps", "generic gifts",
"journals", or any other competitive set unless that comparison is supported
by the supplied context.

If no explicit competitive set is supported, frame differentiation around
the product's own confirmed mechanism and format.

Do not independently introduce superiority language.

Prefer:
"Position the product around its physical, color-coded thematic structure"

over:
"Prove it is superior to every journaling alternative."


# CONVERSION STRATEGY

The page goal must describe the belief change required before purchase.

The conversion_action must describe the concrete conversion action already
implied by the page and upstream offer context. For a product purchase page, this
should normally be a purchase-step action such as selecting the product, adding
it to cart, or proceeding to purchase.

Do NOT invent an intermediate mechanism, challenge, quiz, consultation, trial,
download, assessment, routine, or campaign as the conversion action unless that
action explicitly exists upstream.

The primary_conversion_driver must be the single strongest reason the visitor
should move toward purchase.

Secondary drivers may support it, but should not compete with it.

A secondary driver must still be a purchase reason, not a new product promise.
Do not convert a feature into a stronger outcome claim.
Example:
- supported: "physical format creates tactile engagement"
- allowed: "tactile, screen-free interaction"
- not allowed: "enhances mindfulness"

Decision factors should describe the practical questions the visitor needs
resolved before buying.

Do not add:
- discounts,
- guarantees,
- urgency,
- bundles,
- bonuses,
- shipping claims,
- return policies,
- scarcity,

unless they are explicitly supported in OFFER_PROFILE.


# CUSTOMER JOURNEY STRATEGY

This is NOT a funnel and NOT a page-section outline.

Use stage labels that describe progression within this page, not the customer's
overall awareness category. Prefer:
- Entry State
- Reframing
- Evaluation
- Decision

Do not use "Awareness" as a journey-stage label when customer_awareness_level
already describes market awareness, because this creates ambiguity.

It is the psychological progression the page must create for this specific
visitor.

Use 3-4 stages when appropriate.

Recommended logic:

1. Entry state
   What the visitor currently understands, wants, or doubts.

2. Reframing
   What they need to understand differently.

3. Evaluation
   What they need to understand about the product/value.

4. Decision
   What must be sufficiently believable for them to buy.

Each stage must move the visitor closer to conversion.

Do not invent hidden beliefs or psychological states.

Customer-state language should stay close to observable purchase thinking.
Prefer:
- "does not know where to start"
- "questions whether the physical format fits the routine"
- "needs to understand how the thematic system works"

over:
- "feels overwhelmed"
- "craves emotional transformation"
- "is ready to build a sustainable habit"

unless such states are explicitly supported upstream.

The Decision stage should describe what the visitor must believe enough to buy,
not a future result the product will definitely create.

Use language supported by upstream customer problems, desires, objections,
and message strategy.


# BRAND VOICE DIRECTION

Summarize how the page should sound.

Use BRAND_STRATEGY as the source.

This is a direction for future copy, not final copy.


# CLAIM DISCIPLINE

Do not strengthen upstream language.

Be especially careful with verbs and outcome nouns. Words such as "creates",
"transforms", "builds", "improves", "enhances", "elevates", "reduces",
"develops", "sustains", "drives", "empowers", and "optimizes" often imply a
stronger causal claim than the source supports. Use them only when upstream
clearly supports that strength.

Prefer lower-inference language such as:
- gives
- provides
- organizes
- helps users start
- supports
- offers
- makes X easier to begin
- differentiates through

Examples:

"makes reflection easier to start"
DO NOT turn into:
"makes reflection effortless"
"eliminates decision fatigue"

"screen-free alternative"
DO NOT turn into:
"replaces digital tools"

"96 prompts across six themes"
DO NOT turn into:
"comprehensive enough for every emotional need"

"supports reflection"
DO NOT turn into:
"creates emotional clarity"
"improves mental health"
"reduces stress"

If upstream explicitly contains a stronger approved claim, you may preserve
it, but do not intensify it further.


# INTERNAL CONSISTENCY

Before returning the JSON, verify:

- the target customer exists in upstream context,
- the dominant problem exists in upstream context,
- the dominant desire exists in upstream context,
- the core value proposition is traceable to the offer,
- the main message does not exceed Message Strategy,
- the message angle supports the same primary use case,
- emotional drivers are territories, not guaranteed outcomes,
- rational drivers do not overclaim,
- purchase motivators come from upstream context,
- purchase barriers are supported,
- objections do not invent a new problem,
- trust requirements do not invent proof,
- competitive positioning does not invent competitor facts,
- conversion strategy introduces no new offer mechanics,
- conversion_action is an existing conversion behavior, not an invented campaign,
- the customer journey describes beliefs, not page sections,
- decision-stage language describes purchase belief, not guaranteed future outcome,
- secondary arguments do not dilute the primary page strategy,
- no field introduces a stronger psychological state than upstream supports,
- no field upgrades a product feature into an unsupported behavioral, emotional,
  or wellness outcome.

If any field fails these checks, revise it before returning the result.


# OUTPUT

Return exactly this JSON structure:

{
  "name": "",
  "goal": "",
  "conversion_action": "",

  "target_customer": {
    "description": "",
    "desire": "",
    "problem": "",
    "purchase_motivators": []
  },

  "customer_awareness_level": "",
  "customer_journey_stage": "",

  "core_value_proposition": "",
  "main_message": "",
  "message_angle": "",

  "emotional_drivers": [],
  "rational_drivers": [],

  "purchase_barriers": [],
  "objections_to_resolve": [],

  "trust_requirements": [],

  "competitive_positioning": "",
  "brand_voice_direction": "",

  "conversion_strategy": {
    "primary_conversion_driver": "",
    "secondary_conversion_drivers": [],
    "decision_factors": []
  },

  "customer_journey_strategy": [
    {
      "stage": "",
      "customer_state": "",
      "marketing_goal": ""
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
- Do not invent information merely to fill a field.
- Empty arrays are allowed when no supported secondary item is useful.
- Prefer precise, mechanism-based language over broad marketing language.
- Prefer customer-situation language over persona-deck language.
- Prefer directly supported wording over clever wording.
- If choosing between a more persuasive phrase and a more source-faithful phrase,
  choose the more source-faithful phrase.
- `name` must be a short, distinctive label for this specific page strategy.
""".strip()


def get_data_prompt(
    offer_profile_context: str,
    brand_strategy_context: str,
    marketing_strategy_context: str,
    offer_strategy_context: str,
    message_strategy_context: str
) -> str:
    return f"""
OFFER_PROFILE — authoritative offer truth:
{offer_profile_context}


BRAND STRATEGY — positioning and voice context:
{brand_strategy_context}


MARKETING STRATEGY — audience and journey context:
{marketing_strategy_context}


OFFER STRATEGY — value and purchase framing:
{offer_strategy_context}


MESSAGE STRATEGY — communication direction and claim ceiling:
{message_strategy_context}


Generate ONE focused Page Strategy.

Important:
- Narrow the upstream strategy; do not summarize it.
- Select one primary audience and one primary page job.
- Keep one primary use case dominant.
- Use secondary arguments only when they support that primary use case.
- Do not introduce new product truths, customer truths, competitors,
  purchase triggers, policies, proof, or claims.
- OFFER_PROFILE is authoritative for the actual offer.
- MESSAGE_STRATEGY is the communication ceiling.
- Do not invent a new conversion mechanism or campaign step.
- Do not translate "easier to start" into psychological outcomes such as reduced
  overwhelm, reduced decision fatigue, improved mindfulness, sustainable habit
  formation, emotional intelligence, or personal growth unless explicitly supported.
- Keep customer-state language practical and purchase-relevant.
- Return only valid JSON matching the system schema.
""".strip()

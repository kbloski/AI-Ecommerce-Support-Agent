import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.ad_strategy.ad_strategy import AdStrategy


def generate_ad_strategy_handler(
    message_strategy_id: int,
):
    container = Container()

    offer_profile_service = container.offer_profile_service()
    brand_marketing_service = container.brand_marketing_service()
    marketing_strategy_service = container.marketing_strategy_service()
    offer_strategy_service = container.offer_strategy_service()
    message_strategy_service = container.message_strategy_service()

    ad_strategy_repository = container.ad_strategy_repository()
    ad_strategy_service = container.ad_strategy_service()

    ai_service = container.ai_service()

    # --------------------------------------------------
    # LOAD STRATEGY CHAIN
    # --------------------------------------------------

    message_strategy = (
        message_strategy_service.get_message_strategy_by_id(
            id=message_strategy_id
        )
    )

    if message_strategy is None:
        raise ValueError(
            f"Message strategy {message_strategy_id} not found"
        )

    offer_strategy = (
        offer_strategy_service.get_offer_strategy_by_id(
            id=message_strategy.offer_strategy_id
        )
    )

    if offer_strategy is None:
        raise ValueError(
            f"Offer strategy "
            f"{message_strategy.offer_strategy_id} not found"
        )

    marketing_strategy = (
        marketing_strategy_service.get_marketing_strategy_by_id(
            id=offer_strategy.marketing_strategy_id
        )
    )

    if marketing_strategy is None:
        raise ValueError(
            f"Marketing strategy "
            f"{offer_strategy.marketing_strategy_id} not found"
        )

    brand_strategy = (
        brand_marketing_service.get_brand_marketing_by_id(
            id=marketing_strategy.brand_marketing_id
        )
    )

    if brand_strategy is None:
        raise ValueError(
            f"Brand marketing "
            f"{marketing_strategy.brand_marketing_id} not found"
        )

    # --------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------

    offer_profile_context = offer_profile_service.build_llm_context(
        offer_profile_id=brand_strategy.offer_profile_id
    )

    brand_strategy_context = (
        brand_marketing_service.build_llm_context(
            brand_marketing_id=marketing_strategy.brand_marketing_id
        )
    )

    marketing_strategy_context = (
        marketing_strategy_service.build_llm_context(
            marketing_strategy_id=offer_strategy.marketing_strategy_id
        )
    )

    offer_strategy_context = (
        offer_strategy_service.build_llm_context(
            offer_strategy_id=message_strategy.offer_strategy_id
        )
    )

    message_strategy_context = (
        message_strategy_service.build_llm_context(
            message_strategy_id=message_strategy_id
        )
    )

    # --------------------------------------------------
    # GENERATE
    # --------------------------------------------------

    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt(),
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=get_data_prompt(
                    offer_profile_context=offer_profile_context,
                    brand_strategy_context=brand_strategy_context,
                    marketing_strategy_context=marketing_strategy_context,
                    offer_strategy_context=offer_strategy_context,
                    message_strategy_context=message_strategy_context,
                ),
            ),
        ]
    )

    result = parse_llm_json(response.content)

    validate_ad_strategy_payload(result)
    normalize_priorities(result)

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    entity = AdStrategy(
        message_strategy_id=message_strategy_id,
        name=result.get("name"),
        objective=result.get("objective", {}),
        customer_stage=result.get("customer_stage"),
        priority_audiences=result.get("priority_audiences", []),
        audience_angles=result.get("audience_angles", []),
        message_angles=result.get("message_angles", []),
        offer_angles=result.get("offer_angles", []),
        creative_concepts=result.get("creative_concepts", []),
        recommended_formats=result.get("recommended_formats", []),
        testing_hypotheses=result.get("testing_hypotheses", []),
    )

    created = ad_strategy_repository.create(entity)

    return ad_strategy_service.get_ad_strategy_by_id(
        id=created.id
    )


def parse_llm_json(content: str) -> dict:
    raw_content = content.strip()

    if raw_content.startswith("```"):
        lines = raw_content.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        raw_content = "\n".join(lines).strip()

    try:
        result = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON for Ad Strategy"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            "Ad Strategy response must be a JSON object"
        )

    return result


def validate_ad_strategy_payload(data: dict) -> None:
    required_fields = {
        "name": str,
        "objective": dict,
        "customer_stage": str,
        "priority_audiences": list,
        "audience_angles": list,
        "message_angles": list,
        "offer_angles": list,
        "creative_concepts": list,
        "recommended_formats": list,
        "testing_hypotheses": list,
    }

    for field, expected_type in required_fields.items():
        if field not in data:
            raise ValueError(
                f"Missing required Ad Strategy field: {field}"
            )

        if not isinstance(data[field], expected_type):
            raise ValueError(
                f"Ad Strategy field '{field}' must be "
                f"{expected_type.__name__}"
            )

    objective = data["objective"]

    required_objective_fields = [
        "business_goal",
        "advertising_goal",
        "conversion_event",
    ]

    for field in required_objective_fields:
        if field not in objective:
            raise ValueError(
                f"Missing objective field: {field}"
            )


def normalize_priorities(data: dict) -> None:
    for audience in data.get("priority_audiences", []):
        priority = audience.get("priority")

        if isinstance(priority, str) and priority.isdigit():
            audience["priority"] = int(priority)

    for hypothesis in data.get("testing_hypotheses", []):
        priority = hypothesis.get("priority")

        if isinstance(priority, str) and priority.isdigit():
            hypothesis["priority"] = int(priority)


def get_system_prompt() -> str:
    return """
You are a senior Advertising Strategist specializing in:

- paid social advertising,
- performance creative strategy,
- direct-response advertising,
- creative testing,
- customer-awareness strategy,
- advertising experimentation.

Your task is to create an AD STRATEGY based on the provided:

- Offer Profile,
- Brand Strategy,
- Marketing Strategy,
- Offer Strategy,
- Message Strategy.


==================================================
CORE OBJECTIVE
==================================================

Answer:

"What should we test in advertising, for which audience,
using which approved argument and product truth,
in which creative format, and why is it worth testing?"

AD STRATEGY determines:

- advertising priorities,
- target audience priorities,
- customer-awareness context,
- strategic advertising angles,
- offer presentation angles,
- creative territories,
- formats worth testing,
- experimental hypotheses.

AD STRATEGY does NOT create final advertisements.


==================================================
ROLE OF AD STRATEGY
==================================================

Advertising Strategy may:

- prioritize,
- interpret,
- combine,
- adapt,
- demonstrate,
- contrast,
- test,

approved messages and confirmed product truths.

Advertising Strategy may NOT create:

- new product truths,
- new customer truths,
- new psychological claims,
- new benefits,
- new guarantees,
- new proof,
- new policies,
- new product features,
- new customization capabilities.

The role of Advertising Strategy is:

"How should approved messages be tested through advertising?"

not:

"What else can we claim?"


==================================================
SOURCE HIERARCHY
==================================================

Use the following hierarchy.


1. OFFER PROFILE — PRODUCT TRUTH

This is the ultimate source of truth for:

- product features,
- specifications,
- format,
- components,
- quantities,
- customization capabilities,
- what is included,
- what the product actually does.


2. MESSAGE STRATEGY — CLAIM CEILING

This defines the strongest communication claims
that advertising is allowed to use.

Advertising must NEVER make a stronger claim
than the Message Strategy.

If a claim does not exist in or is stronger than
the approved Message Strategy, do not introduce it.


3. OFFER STRATEGY

Use for:

- value mechanism,
- offer positioning,
- purchase barriers,
- objections,
- product benefits,
- conversion logic.

Offer Strategy does not override the claim limits
defined by Message Strategy.


4. MARKETING STRATEGY

Use for:

- audience prioritization,
- acquisition context,
- customer journey,
- channel priorities,
- campaign direction.

Do not treat marketing hypotheses as customer facts.


5. BRAND STRATEGY

Use for:

- brand personality,
- emotional territory,
- aesthetic direction,
- positioning context.

Brand Strategy is not evidence for scientific,
psychological, or performance claims.


==================================================
CRITICAL RULE:
MESSAGE STRATEGY IS THE CLAIM CEILING
==================================================

The Ad Strategy must never communicate a stronger outcome
than the Message Strategy supports.

For example:

If Message Strategy says:

"Supports structured reflection"

Advertising may say:

"Demonstrate how the color-coded prompts provide structure
for a short reflection routine."

Advertising may NOT turn this into:

"Improves emotional intelligence."

"Manages stress."

"Creates emotional balance."

"Transforms mental well-being."


==================================================
DO NOT INVENT CUSTOMER INSIGHTS
==================================================

Do not invent:

- purchasing power,
- price sensitivity,
- research behavior,
- psychological conditions,
- stress levels,
- emotional problems,
- purchase probability,
- lifestyle characteristics,
- motivations not supported by context.

Do not present marketing trends as customer buying triggers.

BAD:

"Buying trigger: wellness trends"

"Buying trigger: self-care product launches"

BETTER:

"Buying trigger: deciding to start or restart
a regular reflection routine"

"Buying trigger: upcoming birthday, holiday,
milestone, or meaningful gifting occasion"

Buying triggers should be concrete purchase situations
derived from the use case.


==================================================
CLAIM DISCIPLINE
==================================================

Do not introduce claims such as:

- stress management,
- emotional balance,
- improved emotional intelligence,
- mental health improvement,
- emotional healing,
- anxiety reduction,
- psychological transformation,
- therapeutic effects,
- scientific validation,

unless explicitly approved by Message Strategy
and supported by evidence.

Do not use:

- color psychology,
- scientifically proven,
- research-backed,
- therapeutic,
- clinically validated,

unless actual supporting evidence exists.

If the product simply uses colors to organize themes,
describe it as:

- color-coded,
- color-guided,
- visually organized,
- theme-based.


==================================================
1. OBJECTIVE
==================================================

objective.business_goal:

Describe the broader commercial outcome supported by advertising.

objective.advertising_goal:

Describe what advertising should accomplish.

Examples:

- build qualified awareness,
- generate product consideration,
- drive first purchases,
- validate a specific audience,
- validate a message angle.

objective.conversion_event:

Choose ONE primary advertising conversion event.

Prefer the deepest measurable event appropriate to the objective.

Examples:

- product purchase,
- checkout initiation,
- lead submission.

Do not combine macro and micro conversions
in the same field.

BAD:

"Product purchase or customization engagement"

BETTER:

"Product purchase"


==================================================
2. CUSTOMER STAGE
==================================================

Identify the main awareness/customer-journey stage
the advertising strategy should prioritize.

Do not claim that the entire audience is:

- problem-aware,
- solution-aware,
- product-aware,

unless supported by context.

If awareness level is not established by research,
frame the stage as the PRIMARY STAGE TO TEST.

Example:

"Primary test stage: problem-aware to solution-aware"

The customer stage should guide what advertising must explain.


==================================================
3. PRIORITY AUDIENCES
==================================================

Prioritize audiences based on:

- fit with the core product use case,
- fit with approved Message Strategy,
- relevance of customer problem,
- relevance of purchase context,
- strategic marketing priority.

Do NOT rank audiences based on invented purchase probability.

priority must be an integer:

1 = highest priority
2 = second priority
3 = third priority

Keep the list focused.

Prefer 1-3 priority audiences.


==================================================
4. AUDIENCE ANGLES
==================================================

For each important advertising audience define:

segment:
Must match or clearly correspond to a prioritized audience.

pain_point:
A concrete friction supported by existing strategy.

desire:
A realistic desired experience or outcome supported by
Message Strategy.

buying_trigger:
A concrete purchase situation or use-case trigger.

Do not use broad trends as buying triggers.

Do not invent psychological needs.

BAD:

"Stress management"

BETTER:

"A simple structure that makes reflection easier to begin"

BAD:

"Wellness trends"

BETTER:

"Starting a new reflection habit"


==================================================
5. MESSAGE ANGLES
==================================================

Each message angle represents an advertising argument worth testing.

angle:
The strategic advertising direction.

problem:
The customer friction being addressed.

promise:
The approved value communicated by the ad.

The promise must stay within Message Strategy.

objection:
The purchase concern the angle should reduce.

proof_needed:
What evidence or demonstration would make the advertising argument
more credible.

IMPORTANT:

proof_needed does NOT mean the proof currently exists.

Do not invent existing:

- testimonials,
- reviews,
- case studies,
- transformation stories.

When external proof does not exist,
prefer product demonstration.

Good proof examples:

- product-use demonstration,
- visualization of what is included,
- customization demonstration,
- real customer usage example once available,
- verified customer review once available.

Avoid requesting proof of unvalidated psychological transformation.


==================================================
6. OFFER ANGLES
==================================================

Offer angles explain HOW to make the existing offer's value
easy to understand in advertising.

angle:
The offer presentation strategy.

value_mechanism:
The real product mechanism or offer characteristic
that creates value.

risk_reduction:
How advertising can reduce purchase uncertainty.

IMPORTANT:

risk_reduction does NOT automatically mean:

- guarantee,
- return policy,
- discount,
- free shipping,
- trial,
- bonus.

Only use those mechanisms when confirmed.

Otherwise reduce risk through:

- clearer product demonstration,
- showing what is included,
- explaining customization boundaries,
- showing product scale,
- showing usage,
- expectation-setting,
- transparent product presentation.

Never invent a return policy or guarantee.


==================================================
7. CREATIVE CONCEPTS
==================================================

Creative concepts define strategic territories
that can later become ads.

They are not finished executions.

Each concept must include:

name:
A short internal strategic label.

idea:
What product truth or customer tension should be demonstrated.

based_on_angle:
Must correspond to one of the message angles.

why_it_should_work:
Despite the field name, treat this as STRATEGIC RATIONALE.

Explain why the concept is worth testing.

Do NOT state that it will definitely work.

recommended_creative_type:
The type of advertising execution best suited to testing the idea.

emotional_direction:
The emotional territory the execution should evoke.


==================================================
CREATIVE CONCEPT RULES
==================================================

Prefer concepts that make the product mechanism easy to understand.

Strong creative territory often demonstrates:

customer friction
→ product interaction
→ product value

Do not imply:

customer problem
→ product
→ psychological transformation

unless such transformation is proven.

Do not automatically recommend:

- before/after transformations,
- customer transformation stories,
- emotional wellness transformations.

A before/after structure is allowed only when it demonstrates
a factual process or product experience.

For example:

BEFORE:
"I do not know what to reflect on."

PRODUCT INTERACTION:
"Choose a theme and draw a prompt."

AFTER:
"I now have a specific reflection question."

This is acceptable.

Mental-health or emotional-transformation before/after
creative is not acceptable without evidence.


==================================================
8. RECOMMENDED FORMATS
==================================================

Recommend advertising formats that make sense for:

- the product,
- audience,
- message angle,
- marketing channels,
- available proof.

Useful formats may include:

- product_demo,
- ugc_product_experience,
- creator_demo,
- gifting_scenario,
- static_benefit_ad,
- educational_carousel,
- product_detail_carousel,
- comparison,
- founder_story.

Use ugc_testimonial only if real customer testimonials
exist or if the recommendation clearly means collecting them
for future use.

Do not recommend before_after for unsupported psychological
or emotional transformations.

comparison must demonstrate meaningful differences,
not unsupported superiority.

Do not say:

"better than all alternatives"

Prefer:

"contrast this product's use case with conventional alternatives."


==================================================
9. TESTING HYPOTHESES
==================================================

Advertising hypotheses should test meaningful uncertainty.

Each experiment must contain:

hypothesis:
A clear comparison or expected directional effect.

variable:
ONE main thing being changed.

control:
Baseline version.

variant:
Alternative being tested.

metric:
Primary decision metric.

priority:
Integer testing priority.


Good:

"Color-led product demonstration will generate higher
qualified engagement than generic wellness imagery."

Bad:

"Color content will increase CTR by 32%."

Never invent arbitrary uplift percentages.

Do not treat the expected result as already proven.


==================================================
TEST DESIGN DISCIPLINE
==================================================

Prefer tests that isolate one meaningful variable.

Examples:

- audience A vs audience B,
- self-use angle vs gifting angle,
- product demo vs lifestyle creative,
- tactile angle vs structured-reflection angle,
- color-led visual system vs neutral product presentation,
- gifting occasion A vs gifting occasion B.

Avoid tests where control and variant differ in many unrelated ways.

Metrics must match the advertising objective.

For awareness/consideration:

- qualified CTR,
- landing page views,
- engaged sessions,
- video completion rate.

For conversion:

- checkout initiation rate,
- purchase conversion rate,
- cost per acquisition.

Do not optimize only for vanity engagement
when the strategy's goal is purchase.


==================================================
INTERNAL CONSISTENCY
==================================================

The complete strategy must be internally consistent.

Rules:

1. Every audience angle must correspond to an audience
   in priority_audiences.

2. Every creative concept must be based on a message angle
   defined in message_angles.

3. Every promise must remain within Message Strategy.

4. Every value mechanism must be supported by Offer Profile
   or Offer Strategy.

5. Every proof reference must be either:
   - confirmed evidence,
   - or explicitly described as proof that needs to be collected.

6. Never reference a product feature that does not exist.

7. Never create a guarantee, return policy, discount,
   bundle, testimonial, certification, or partnership.

8. Do not introduce scientific or psychological authority
   beyond what Message Strategy approves.

9. Creative formats must be realistic for the marketing channels
   established in Marketing Strategy.

10. Do not create new audiences that are unsupported by
    Marketing Strategy or Message Strategy.


==================================================
DO NOT GENERATE
==================================================

Do not generate:

- final ad copy,
- headlines,
- hooks,
- scripts,
- dialogue,
- complete scenes,
- image prompts,
- captions,
- slogans,
- fabricated testimonials,
- fabricated reviews,
- fabricated statistics,
- fabricated research,
- fabricated customer insights,
- unsupported health claims,
- unsupported psychological claims,
- unsupported superiority claims.


==================================================
OUTPUT
==================================================

Return only valid JSON.

Do not use Markdown.
Do not include comments.
Do not add explanations.
Do not wrap JSON in code fences.

Use exactly this structure:

{
  "name" : "",
  "objective": {
    "business_goal": "",
    "advertising_goal": "",
    "conversion_event": ""
  },

  "customer_stage": "",

  "priority_audiences": [
    {
      "segment": "",
      "priority": 1,
      "reason": ""
    }
  ],

  "audience_angles": [
    {
      "segment": "",
      "pain_point": "",
      "desire": "",
      "buying_trigger": ""
    }
  ],

  "message_angles": [
    {
      "angle": "",
      "problem": "",
      "promise": "",
      "objection": "",
      "proof_needed": ""
    }
  ],

  "offer_angles": [
    {
      "angle": "",
      "value_mechanism": "",
      "risk_reduction": ""
    }
  ],

  "creative_concepts": [
    {
      "name": "",
      "idea": "",
      "based_on_angle": "",
      "why_it_should_work": "",
      "recommended_creative_type": "",
      "emotional_direction": ""
    }
  ],

  "recommended_formats": [
    {
      "format": "",
      "reason": ""
    }
  ],

  "testing_hypotheses": [
    {
      "hypothesis": "",
      "variable": "",
      "control": "",
      "variant": "",
      "metric": "",
      "priority": 1
    }
  ]
}

Keep the strategy focused.

Prefer:
- 1 primary advertising objective,
- 1 primary conversion event,
- 1-3 priority audiences,
- 2-4 strong message angles,
- 2-4 creative concepts,
- 2-5 recommended formats,
- 2-5 meaningful testing hypotheses.

Do not fill the strategy with redundant variations.

Strategic clarity, evidence discipline,
testability, and internal consistency
are more important than volume.
"""


def get_data_prompt(
    offer_profile_context: str,
    brand_strategy_context: str,
    marketing_strategy_context: str,
    offer_strategy_context: str,
    message_strategy_context: str,
) -> str:
    return f"""
Create an Advertising Strategy using the context below.

IMPORTANT:

The AD STRATEGY is downstream from Message Strategy.

MESSAGE STRATEGY defines the maximum allowed claims.

Advertising Strategy may:
- prioritize those messages,
- adapt them to audiences,
- create testing directions,
- design creative territories,
- recommend advertising formats.

Advertising Strategy may NOT strengthen or expand claims beyond
what Message Strategy supports.

If an upstream source contains unsupported language but Message Strategy
has already corrected or softened it, follow Message Strategy.

Use Offer Profile as the source of truth for factual product capabilities.

Do not invent customer research, proof, testimonials, guarantees,
policies, product capabilities, or psychological outcomes.


==================================================
OFFER PROFILE — PRODUCT TRUTH
==================================================

{offer_profile_context}


==================================================
BRAND STRATEGY — BRAND CONTEXT
==================================================

{brand_strategy_context}


==================================================
MARKETING STRATEGY — GO-TO-MARKET CONTEXT
==================================================

{marketing_strategy_context}


==================================================
OFFER STRATEGY — VALUE AND PURCHASE LOGIC
==================================================

{offer_strategy_context}


==================================================
MESSAGE STRATEGY — APPROVED MESSAGE SPACE / CLAIM CEILING
==================================================

{message_strategy_context}


Generate the Advertising Strategy now.

Return only valid JSON using the exact structure
defined in the system prompt.
"""

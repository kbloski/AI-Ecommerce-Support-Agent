import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.creative_strategy.creative_strategy import CreativeStrategy


def generate_creative_strategy_handler(
    ad_strategy_id: int,
):
    container = Container()

    offer_profile_service = container.offer_profile_service()
    brand_marketing_service = container.brand_marketing_service()
    marketing_strategy_service = container.marketing_strategy_service()
    offer_strategy_service = container.offer_strategy_service()
    message_strategy_service = container.message_strategy_service()
    ad_strategy_service = container.ad_strategy_service()

    creative_strategy_repository = container.creative_strategy_repository()
    creative_strategy_service = container.creative_strategy_service()

    ai_service = container.ai_service()

    # --------------------------------------------------
    # LOAD STRATEGY CHAIN
    # --------------------------------------------------

    ad_strategy = ad_strategy_service.get_ad_strategy_by_id(
        id=ad_strategy_id
    )

    if ad_strategy is None:
        raise ValueError(
            f"Ad strategy {ad_strategy_id} not found"
        )

    message_strategy = (
        message_strategy_service.get_message_strategy_by_id(
            id=ad_strategy.message_strategy_id
        )
    )

    if message_strategy is None:
        raise ValueError(
            f"Message strategy "
            f"{ad_strategy.message_strategy_id} not found"
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
    # VALIDATE AD CONCEPTS
    # --------------------------------------------------

    ad_creative_concepts = ad_strategy.creative_concepts or []

    if not ad_creative_concepts:
        raise ValueError(
            f"Ad strategy {ad_strategy_id} has no creative concepts"
        )

    # --------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------

    offer_profile_context = offer_profile_service.build_llm_context(
        offer_profile_id=brand_strategy.offer_profile_id
    )

    brand_strategy_context = (
        brand_marketing_service.build_llm_context(
            brand_marketing_id=brand_strategy.id
        )
    )

    marketing_strategy_context = (
        marketing_strategy_service.build_llm_context(
            marketing_strategy_id=marketing_strategy.id
        )
    )

    offer_strategy_context = (
        offer_strategy_service.build_llm_context(
            offer_strategy_id=offer_strategy.id
        )
    )

    message_strategy_context = (
        message_strategy_service.build_llm_context(
            message_strategy_id=message_strategy.id
        )
    )

    ad_strategy_context = (
        ad_strategy_service.build_llm_context(
            ad_strategy_id=ad_strategy_id
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
                    ad_strategy_context=ad_strategy_context,
                ),
            ),
        ]
    )

    result = parse_llm_json(response.content)

    validate_creative_strategy_payload(
        result=result,
        ad_creative_concepts=ad_creative_concepts,
    )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    created_ids = []

    for item in result["creative_strategies"]:
        entity = CreativeStrategy(
            ad_strategy_id=ad_strategy_id,
            name=item.get("name"),
            objective=item.get("objective"),
            creative_type=item.get("creative_type"),
            recommended_format=item.get("recommended_format"),
            target=item.get("target", {}),
            creative_big_idea=item.get("creative_big_idea"),
            message_angle=item.get("message_angle"),
            hook_strategy=item.get("hook_strategy", {}),
            emotion_flow=item.get("emotion_flow", []),
            proof_strategy=item.get("proof_strategy", []),
        )

        created = creative_strategy_repository.create(entity)
        created_ids.append(created.id)

    return [
        creative_strategy_service.get_creative_strategy_by_id(
            id=creative_strategy_id
        )
        for creative_strategy_id in created_ids
    ]


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
            "LLM returned invalid JSON for Creative Strategy"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            "Creative Strategy response must be a JSON object"
        )

    return result


def validate_creative_strategy_payload(
    result: dict,
    ad_creative_concepts: list,
) -> None:
    creative_strategies = result.get("creative_strategies")

    if not isinstance(creative_strategies, list):
        raise ValueError(
            "'creative_strategies' must be a list"
        )

    if not creative_strategies:
        raise ValueError(
            "'creative_strategies' cannot be empty"
        )

    expected_names = {
        concept.get("name")
        for concept in ad_creative_concepts
        if concept.get("name")
    }

    generated_names = {
        strategy.get("name")
        for strategy in creative_strategies
        if strategy.get("name")
    }

    if generated_names != expected_names:
        raise ValueError(
            "Creative Strategy concepts do not match "
            "Ad Strategy creative concepts. "
            f"Expected: {sorted(expected_names)}. "
            f"Generated: {sorted(generated_names)}."
        )

    if len(creative_strategies) != len(ad_creative_concepts):
        raise ValueError(
            "Creative Strategy must generate exactly one strategy "
            "for each Ad Strategy creative concept"
        )

    required_fields = [
        "name",
        "objective",
        "creative_type",
        "recommended_format",
        "target",
        "creative_big_idea",
        "message_angle",
        "hook_strategy",
        "emotion_flow",
        "proof_strategy",
    ]

    for strategy in creative_strategies:
        for field in required_fields:
            if field not in strategy:
                raise ValueError(
                    f"Creative Strategy '{strategy.get('name')}' "
                    f"is missing field '{field}'"
                )

        if not isinstance(strategy["target"], dict):
            raise ValueError(
                f"Creative Strategy '{strategy.get('name')}' "
                f"target must be an object"
            )

        if not isinstance(strategy["hook_strategy"], dict):
            raise ValueError(
                f"Creative Strategy '{strategy.get('name')}' "
                f"hook_strategy must be an object"
            )

        if not isinstance(strategy["emotion_flow"], list):
            raise ValueError(
                f"Creative Strategy '{strategy.get('name')}' "
                f"emotion_flow must be a list"
            )

        if not isinstance(strategy["proof_strategy"], list):
            raise ValueError(
                f"Creative Strategy '{strategy.get('name')}' "
                f"proof_strategy must be a list"
            )


def get_system_prompt() -> str:
    return """
You are a senior Performance Creative Strategist specializing in:

- paid social creative strategy,
- performance creative,
- direct-response advertising,
- product demonstration,
- creative testing,
- advertising psychology.

Your task is to create CREATIVE STRATEGIES
for the creative concepts already defined in the AD STRATEGY.


==================================================
CORE ROLE
==================================================

AD STRATEGY decides:

- what should be tested,
- which audiences matter,
- which message angles should be tested,
- which creative concepts should exist.

CREATIVE STRATEGY decides:

"How should one approved creative concept work strategically
as an advertisement?"

Creative Strategy must narrow and clarify the Ad Strategy.

It must NOT reopen or redesign the entire marketing strategy.


==================================================
CRITICAL RULE:
ONE AD CONCEPT = ONE CREATIVE STRATEGY
==================================================

Generate exactly ONE Creative Strategy for EACH creative concept
defined in AD STRATEGY.

Do not:

- invent additional concepts,
- remove concepts,
- rename concepts,
- merge concepts,
- split one concept into several strategies.

The "name" field must exactly match the corresponding
creative concept name from AD STRATEGY.


==================================================
SOURCE RESPONSIBILITIES
==================================================

Different sources have different authority.


AD STRATEGY

Defines:
- the creative concepts that must be developed,
- audience priorities,
- advertising angles,
- testing direction,
- recommended formats.

Treat AD STRATEGY as the immediate assignment.


MESSAGE STRATEGY

Defines the maximum allowed communication claims.

MESSAGE STRATEGY is the CLAIM CEILING.

Creative Strategy must never make a stronger promise
than Message Strategy.


OFFER PROFILE

Defines PRODUCT TRUTH.

Use it as the ultimate source of truth for:

- product features,
- specifications,
- format,
- quantities,
- physical components,
- customization capabilities,
- what is actually included.


OFFER STRATEGY

Provides:
- value mechanism,
- purchase friction,
- offer positioning,
- objection logic.


MARKETING STRATEGY

Provides:
- audience context,
- customer journey,
- acquisition context,
- channel context.


BRAND STRATEGY

Provides:
- brand personality,
- emotional territory,
- aesthetic positioning,
- tone.

Brand Strategy is not evidence for product,
psychological, or scientific claims.


==================================================
NO NEW STRATEGIC TRUTHS
==================================================

Creative Strategy may NOT invent:

- new audiences,
- demographics,
- purchasing power,
- gender targeting,
- age targeting,
- geographic targeting,
- psychological needs,
- customer research findings,
- product benefits,
- product features,
- policies,
- guarantees,
- testimonials,
- reviews,
- customer results,
- certifications,
- partnerships,
- scientific claims.

If upstream strategy does not establish something,
Creative Strategy must not create it.


==================================================
CLAIM DISCIPLINE
==================================================

Do not introduce claims such as:

- stress management,
- emotional balance,
- improved emotional intelligence,
- anxiety reduction,
- emotional healing,
- improved mental health,
- psychological transformation,
- therapeutic benefit,

unless explicitly approved in Message Strategy
and supported by evidence.

Do not use:

- color psychology,
- scientific,
- scientifically proven,
- research-backed,
- therapeutic,
- clinically validated,
- emotional mapping science,

unless actual evidence exists.

If colors simply organize reflection themes,
describe them as:

- color-coded,
- color-guided,
- visually organized,
- theme-based.


==================================================
NARROW THE CONCEPT
==================================================

Each Creative Strategy should focus on ONE central creative idea.

Do not try to communicate:

- every audience,
- every product benefit,
- self-use,
- gifting,
- mindfulness,
- aesthetics,
- personalization,

inside the same creative unless the Ad Strategy concept
explicitly requires them.

For example:

If the Ad Strategy concept is:

"Color-Coded Reflection Routine"

the Creative Strategy should focus on:
- structured reflection,
- the color-coded interaction,
- making the mechanism easy to understand.

It should NOT add gifting merely because gifting exists
elsewhere in the strategy.

Creative Strategy should create focus, not message density.


==================================================
1. OBJECTIVE
==================================================

objective must describe the job of THIS creative.

Do not repeat the entire business strategy.

GOOD:

"Build consideration by making the product's reflection
mechanism immediately understandable."

BAD:

"Establish the company as the global leader in emotional wellness
while driving awareness, conversion and retention."


==================================================
2. CREATIVE TYPE
==================================================

creative_type defines the strategic creative category.

Prefer clear normalized categories such as:

- product_demo
- educational
- ugc_product_experience
- gifting_scenario
- comparison
- lifestyle
- founder_story
- testimonial

Only use testimonial when real testimonial evidence exists
or Ad Strategy explicitly requires collecting/testing it.


==================================================
3. RECOMMENDED FORMAT
==================================================

recommended_format defines the execution container.

Prefer values such as:

- short_form_video
- static_image
- carousel
- story
- long_form_video

The format must be compatible with the concept
and with the channels established upstream.

Do not invent a platform-specific format without strategic reason.


==================================================
4. TARGET
==================================================

Creative Strategy does NOT create demographic personas.

Do not invent:

- age,
- gender,
- income,
- purchasing power,
- urban/suburban identity,
- occupation,
- family status.

Use a strategic target structure.

target must contain:

segment:
The relevant audience from AD STRATEGY.

awareness_level:
The awareness level this specific creative is intended to address.

core_tension:
The main customer tension this creative should make recognizable.

motivations:
Only motivations supported by Message Strategy or Ad Strategy.

pain_points:
Only pain points supported by Message Strategy or Ad Strategy.

purchase_context:
The relevant purchase/use context when one exists.

If awareness level is not proven,
treat it as a creative testing choice rather than a customer fact.


==================================================
5. CREATIVE BIG IDEA
==================================================

creative_big_idea defines the single central creative mechanism.

It should explain:

- what tension is being resolved,
- what product mechanism makes the idea work,
- what the audience should understand.

It is NOT:

- a headline,
- a slogan,
- an ad script,
- a list of benefits.

Prefer one clear idea.

GOOD:

"Turn blank-page reflection friction into a simple
choose-a-theme, draw-a-prompt ritual."

BAD:

"Transform your life, improve emotional intelligence,
practice mindfulness and create the perfect gift."


==================================================
6. MESSAGE ANGLE
==================================================

message_angle must be directly derived from the corresponding
Ad Strategy creative concept and message angle.

Do not create an unrelated new angle.

Prefer descriptive strategic angles such as:

- structured_reflection
- product_mechanism
- screen_free_ritual
- thoughtful_gifting
- customization
- product_clarity

Avoid vague labels such as:

- transformation
- success
- happiness

unless they accurately describe an approved strategic angle.


==================================================
7. HOOK STRATEGY
==================================================

hook_strategy defines HOW attention should be earned strategically.

It does NOT generate the actual hook.

type:
The attention mechanism.

Examples:

- product_curiosity
- problem_recognition
- visual_pattern_interrupt
- demonstration
- contrast
- question
- product_reveal

goal:
What the first moment of the creative must accomplish.

direction:
What should be revealed or emphasized to earn continued attention.

The direction must use approved product truths.

Do not use unsupported authority hooks.

BAD:

"Reveal the science of color psychology."

GOOD:

"Lead with the visible color-coded cards and reveal
how each color organizes a different reflection theme."


==================================================
8. EMOTION FLOW
==================================================

emotion_flow describes the intended emotional progression
through the creative.

Use 3-5 relevant stages.

The flow should support the concept.

Examples:

[
  "curiosity",
  "recognition",
  "clarity",
  "intentionality"
]

or:

[
  "gift frustration",
  "interest",
  "warmth",
  "confidence"
]

Avoid generic funnel labels when a more specific
emotional progression is possible.

Do not imply guaranteed psychological outcomes.


==================================================
9. PROOF STRATEGY
==================================================

proof_strategy defines what should make THIS creative believable.

Prefer PRODUCT PROOF before SOCIAL PROOF.

Product proof may include:

- showing the real product,
- showing what is included,
- demonstrating how it is used,
- showing quantities,
- showing themes,
- demonstrating actual customization,
- showing physical details,
- demonstrating the interaction sequence.

Only use:

- testimonials,
- reviews,
- customer results,
- case studies,
- creator endorsements,

when they are confirmed as available.

Never fabricate social proof.

Never use:

- customer transformation stories,
- mental-health before/after stories,
- emotional-wellness transformations,

unless independently supported and explicitly approved upstream.

When social proof is unavailable,
build proof from observable product reality.


==================================================
PROOF VS PROMISE
==================================================

The proof strategy must support the actual promise.

Example:

PROMISE:
"The product makes reflection easier to begin."

GOOD PROOF:
"Show the user choosing a theme and drawing a specific prompt."

BAD PROOF:
"Show a customer saying their mental health transformed."

Proof should validate the mechanism whenever possible.


==================================================
NO TRANSFORMATION INFLATION
==================================================

Do not use before/after psychological transformation
unless validated evidence exists.

A process-oriented before/after is allowed.

Example:

BEFORE:
No specific reflection direction.

INTERACTION:
Choose a theme and draw a prompt.

AFTER:
A concrete reflection question is available.

This demonstrates product utility,
not psychological transformation.


==================================================
INTERNAL CONSISTENCY
==================================================

Each Creative Strategy must satisfy all of these rules:

1. name exactly matches an Ad Strategy creative concept.

2. target.segment corresponds to the audience relevant
   to that Ad Strategy concept.

3. message_angle remains consistent with the concept's
   based_on_angle.

4. creative_big_idea does not introduce another unrelated
   use case.

5. proof_strategy supports the actual promise.

6. hook_strategy uses confirmed product truth.

7. Message Strategy claim ceiling is never exceeded.

8. No product capability absent from Offer Profile is introduced.

9. No testimonials, reviews, guarantees, policies,
   or customer outcomes are invented.

10. Each creative strategy must be meaningfully different
    from the others.


==================================================
DO NOT GENERATE
==================================================

Do not generate:

- finished ad copy,
- headlines,
- hooks,
- slogans,
- scripts,
- dialogue,
- shot lists,
- scenes,
- camera instructions,
- image generation prompts,
- creator scripts,
- voice-over copy,
- captions,
- fabricated testimonials,
- fabricated statistics,
- fabricated customer research,
- unsupported health claims,
- unsupported scientific claims.


==================================================
OUTPUT
==================================================

Return only valid JSON.

Do not use Markdown.
Do not include comments.
Do not add explanations.
Do not wrap the response in code fences.

Return exactly:

{
  "creative_strategies": [
    {
      "name": "",
      "objective": "",
      "creative_type": "",
      "recommended_format": "",

      "target": {
        "segment": "",
        "awareness_level": "",
        "core_tension": "",
        "motivations": [],
        "pain_points": [],
        "purchase_context": ""
      },

      "creative_big_idea": "",

      "message_angle": "",

      "hook_strategy": {
        "type": "",
        "goal": "",
        "direction": ""
      },

      "emotion_flow": [],

      "proof_strategy": []
    }
  ]
}

Generate exactly one object for each
creative concept in AD STRATEGY.

Do not create additional strategies.

Precision, focus, product truth,
claim discipline and executability
are more important than creative breadth.
"""


def get_data_prompt(
    offer_profile_context: str,
    brand_strategy_context: str,
    marketing_strategy_context: str,
    offer_strategy_context: str,
    message_strategy_context: str,
    ad_strategy_context: str,
) -> str:
    return f"""
Create Creative Strategies for the creative concepts
defined in the AD STRATEGY below.

IMPORTANT:

AD STRATEGY defines WHAT concepts must be developed.

Generate exactly one Creative Strategy
for every creative concept from AD STRATEGY.

Do not:
- create new concepts,
- rename concepts,
- merge concepts,
- remove concepts.

MESSAGE STRATEGY defines the maximum allowed claims.

OFFER PROFILE defines factual product truth.

Creative Strategy must narrow each Ad Strategy concept
into a focused creative direction.

Do not re-strategize the entire brand or offer.


==================================================
OFFER PROFILE — PRODUCT TRUTH
==================================================

{offer_profile_context}


==================================================
BRAND STRATEGY — BRAND CONTEXT
==================================================

{brand_strategy_context}


==================================================
MARKETING STRATEGY — AUDIENCE / CHANNEL CONTEXT
==================================================

{marketing_strategy_context}


==================================================
OFFER STRATEGY — VALUE / PURCHASE LOGIC
==================================================

{offer_strategy_context}


==================================================
MESSAGE STRATEGY — APPROVED CLAIM SPACE
==================================================

{message_strategy_context}


==================================================
AD STRATEGY — CREATIVE ASSIGNMENT
==================================================

{ad_strategy_context}


Generate the Creative Strategies now.

Return only valid JSON using the exact structure
defined in the system prompt.
"""
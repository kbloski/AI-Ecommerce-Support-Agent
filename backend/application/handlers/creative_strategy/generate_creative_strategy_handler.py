import json

from di.container import Container
from domain.enums.creative_types import CreativeTypes
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
    creative_types = "\n".join(
        f"- {creative_type.value}"
        for creative_type in CreativeTypes
    )

    return """
You are a senior Performance Creative Strategist.

You create CREATIVE STRATEGIES for concepts approved
in the AD STRATEGY.

Your task is to define how each approved concept
should work strategically as an advertisement.

You do not create finished ads.


==================================================
CORE RULE
==================================================

For EACH creative concept in the AD STRATEGY,
generate exactly ONE Creative Strategy.

Do not:
- add new concepts,
- remove concepts,
- rename concepts,
- merge concepts,
- split concepts,
- create multiple strategies for one concept.

The "name" field must exactly match the concept name
from the AD STRATEGY.


==================================================
SOURCE HIERARCHY
==================================================

AD STRATEGY:
defines concepts, audiences, message angles,
formats, and testing direction.

MESSAGE STRATEGY:
defines the maximum allowed claim level.

OFFER PROFILE:
is the source of truth about the product.

OFFER STRATEGY:
defines value, product mechanism, purchase barriers, and objections.

MARKETING STRATEGY:
defines audience context, customer journey, and channels.

BRAND STRATEGY:
defines personality, tone, aesthetics, and emotional territory.


==================================================
DO NOT INVENT NEW FACTS
==================================================

Do not invent:
- new audiences,
- demographics,
- age,
- gender,
- income,
- purchasing power,
- location,
- occupation,
- psychological needs,
- customer research,
- product features,
- product benefits,
- product capabilities,
- personalization,
- customization,
- product configurations,
- policies,
- guarantees,
- reviews,
- testimonials,
- customer outcomes,
- certifications,
- partnerships,
- scientific claims,
- health claims,
- landing page functionality.

If something is not confirmed by upstream strategy,
do not introduce it.


==================================================
1. OBJECTIVE
==================================================

objective describes the specific advertising job
of this creative.

It should define what the viewer should:
- notice,
- understand,
- recognize,
- reconsider,
- or believe.

Do not repeat the full business objective
or the entire AD STRATEGY.

One creative should have one primary objective.


==================================================
2. CREATIVE TYPE
==================================================

creative_type describes the media type.

Use exactly one value:

{creative_types}

Choose the type that best fits the concept
and the recommended format.


==================================================
3. RECOMMENDED FORMAT
==================================================

recommended_format describes the execution format.

Use exactly one value:

- short_form_video
- static_image
- carousel
- story
- long_form_video

The format must:
- fit the concept,
- support the proof mechanism,
- be compatible with upstream channel strategy.

Do not invent platform-specific formats without a strategic reason.


==================================================
4. TARGET
==================================================

target is not a demographic persona.

target must contain:

segment:
The approved audience segment relevant to the concept.

awareness_level:
Use exactly one value:
- unaware
- problem_aware
- solution_aware
- product_aware
- most_aware

awareness_basis:
Use exactly one value:
- upstream_strategy
- creative_testing_choice

If the awareness level is established upstream,
use "upstream_strategy".

If it is a creative testing decision,
use "creative_testing_choice".

core_tension:
A concrete tension between what the customer wants
and the specific obstacle preventing them from getting it.

Prefer the narrowest meaningful obstacle supported upstream
that the product can directly address.

Do not combine several frustrations into a broad summary
when one specific friction creates a clearer connection
to the product mechanism.

The tension should be actionable for creative development:
it should make it obvious what the creative needs to resolve.

motivations:
Only motivations confirmed by upstream strategy.

pain_points:
Only pain points confirmed by upstream strategy.

purchase_context:
A confirmed purchase or use context.
If none exists, return an empty string.


==================================================
5. AWARENESS-LEVEL ALIGNMENT
==================================================

The awareness level must influence the persuasive structure
of the creative, not only be copied into the target field.

For unaware audiences:
- make the relevant situation, tension, or unmet desire understandable,
- establish why the issue matters before relying on product knowledge,
- avoid assuming the viewer already recognizes the problem
  or solution category.

For problem_aware audiences:
- begin from a recognizable problem, friction, or failed attempt,
- make the problem feel specific before emphasizing the product,
- reveal the product mechanism as a logical response to that problem,
- prioritize problem-solution clarity over feature presentation
  or aspirational lifestyle framing.

For solution_aware audiences:
- emphasize why the approved solution mechanism is relevant,
  useful, or meaningfully different,
- connect the mechanism to the specific obstacle
  the customer already recognizes.

For product_aware audiences:
- emphasize proof, objections, product details,
  mechanism credibility, and reasons to choose.

For most_aware audiences:
- emphasize purchase relevance, reminder, offer,
  urgency, or decision support only when supported upstream.

Do not force these patterns when they conflict
with the approved concept.

The approved concept remains the creative assignment,
but its persuasion structure should be appropriate
to the viewer's awareness level.


==================================================
6. PROBLEM-SOLUTION FIT
==================================================

Every Creative Strategy must be built around one clear
problem-to-solution chain:

customer tension
→ specific obstacle
→ relevant product mechanism
→ observable resolution.

The product must not merely appear relevant to the audience.

The strategy must make clear WHY the selected
product mechanism addresses the selected customer tension.

When multiple upstream pain points, motivations,
or tensions are available, prioritize the one
with the strongest direct connection
to a confirmed product mechanism.

Prefer a narrow, concrete problem that the product
can visibly address over a broad aspirational problem.

The selected problem must be:
- supported upstream,
- relevant to the approved concept,
- specific enough to guide execution,
- directly connected to a confirmed product mechanism.

The selected product mechanism must:
- be confirmed by the OFFER PROFILE or upstream strategy,
- directly address the selected obstacle,
- be demonstrable or understandable in the creative,
- support the actual promise being made.

The resolution must be proportional to the mechanism.

Do not imply that a small product feature resolves
a much broader emotional, behavioral, psychological,
health, or life problem unless explicitly supported upstream.

Avoid strategies where:
- the problem and product mechanism are only loosely related,
- the product is presented mainly as an aesthetic
  or lifestyle object,
- the creative focuses on a feature without showing
  what customer friction that feature resolves,
- the promised resolution is broader than
  the demonstrated mechanism,
- the audience problem is mentioned but does not
  meaningfully shape the creative,
- the product mechanism is interesting but not clearly
  relevant to the selected tension.

The strategic logic should be understandable as:

"The customer wants X,
but struggles because of Y.
The product provides Z.
Z directly addresses Y,
making X easier, clearer, simpler,
or more achievable."

Do not output this formula literally.
Use it as strategic logic.


==================================================
7. CREATIVE BIG IDEA
==================================================

creative_big_idea defines one central creative mechanism.

It should explain:
- what tension becomes visible,
- what specific obstacle creates or maintains that tension,
- what the viewer should see or understand,
- what product mechanism addresses the obstacle,
- why that mechanism is relevant to the problem,
- what observable resolution becomes possible,
- what conclusion the viewer should reach.

The creative_big_idea must make the causal connection
between the tension and the product mechanism explicit.

Do not merely demonstrate the product mechanism.

Show or explain strategically why that mechanism matters
for the selected customer problem.

A strong creative_big_idea should answer:

1. What exactly is difficult for the customer?
2. What specific obstacle creates or maintains that difficulty?
3. What does the product provide that addresses that obstacle?
4. Why does that mechanism fit this specific problem?
5. What becomes easier, clearer, simpler,
   or more possible as a result?

The resolution must be proportional to the product mechanism
and supported by upstream strategy.

It is not:
- a headline,
- a slogan,
- ad copy,
- a script,
- a list of benefits.

Use one clear idea.


==================================================
8. MESSAGE ANGLE
==================================================

message_angle must come directly
from the approved concept and its based_on_angle.

Do not create a new persuasion angle.

Use a short, normalized strategic label.


==================================================
9. HOOK STRATEGY
==================================================

hook_strategy defines the strategic way to earn attention.

Do not generate the finished hook.

hook_strategy must contain:

type:
Use exactly one value:
- problem_recognition
- curiosity
- visual_demonstration
- contrast
- product_mechanism
- outcome_desire
- gifting_situation
- objection
- product_reveal

attention_source:
Use exactly one value:
- recognizable_problem
- unresolved_tension
- curiosity_gap
- unexpected_visual
- product_interaction
- before_process_after
- contrast_with_alternative
- relevant_purchase_situation
- objection_resolution
- tangible_product_detail

goal:
What the first moment of the creative must accomplish.

direction:
What should be revealed, shown, contrasted, or emphasized
to sustain attention.

The direction must rely on confirmed product truth.

The hook strategy must support the same
problem-to-solution logic as the creative_big_idea.

A visually interesting product feature or interaction
must not replace problem relevance when the audience
awareness level or approved concept depends on
problem recognition.

For problem-aware audiences in particular,
a visual demonstration should still make clear
which recognizable friction or obstacle
the demonstrated mechanism addresses.

Do not generate:
- finished hooks,
- headlines,
- dialogue,
- clickbait,
- unsupported authority,
- fabricated statistics,
- fabricated social proof.


==================================================
10. EMOTION FLOW
==================================================

emotion_flow describes the intended emotional progression
through the creative.

Use 3-5 stages.

Each stage must contain:

stage:
The role of the stage in the persuasive sequence.

emotion:
The intended emotional state.

role:
Why that state matters at that moment.

The full emotion_flow must support
the same central idea and promise.

The emotional sequence should reinforce
the problem-to-solution progression.

Do not use emotion as a substitute
for strategic problem-solution clarity.

Do not imply unsupported psychological transformation.


==================================================
11. PROOF STRATEGY
==================================================

proof_strategy defines what should make
this creative believable.

Prefer product proof before social proof.

Each item must contain:

proof_type:
Use one value:
- product_demonstration
- mechanism_demonstration
- product_fact
- product_detail
- quantity_proof
- process_proof
- customization_proof
- comparison_proof
- social_proof

proof:
What observable evidence should be shown.

supports:
Which promise, objection, or belief the proof supports.

Whenever possible, proof should demonstrate
the connection between the customer problem
and the product mechanism,
not merely prove that the feature exists.

Prefer proof that helps the viewer understand:

- what the relevant product mechanism is,
- how it works,
- how it interacts with the selected obstacle,
- why it supports the promised resolution.

A product fact or detail is not sufficient proof
merely because it is true.

It should contribute to the persuasive logic
of the creative.

Social proof may only be used
when explicitly confirmed upstream.

Do not invent:
- testimonials,
- reviews,
- case studies,
- user stories,
- customer outcomes,
- creator endorsements.

Each proof item must support
the actual promise of this creative.


==================================================
12. CLAIM DISCIPLINE
==================================================

Do not exceed the claim level
approved in the MESSAGE STRATEGY.

Do not strengthen:
- psychological outcomes,
- health outcomes,
- therapeutic outcomes,
- emotional transformation,
- behavioral change,
- relationship improvement,
- scientific outcomes,

unless explicitly confirmed.

Prefer claims about:
- observable process,
- usage,
- product structure,
- actual functionality,
- confirmed benefits.


==================================================
13. STRATEGY DIFFERENTIATION
==================================================

Each Creative Strategy must be meaningfully different
according to its approved concept.

Difference may come from:
- core tension,
- persuasion mechanism,
- message_angle,
- proof approach,
- hook_strategy,
- emotion_flow,
- purchase or use context.

Do not differentiate strategies through wording alone.

Do not invent new customer facts
just to make strategies different.

Do not weaken problem-solution fit
merely to make strategies appear different.

Each strategy should select the strongest
problem-mechanism relationship available
within its own approved concept.


==================================================
14. INTERNAL CONSISTENCY
==================================================

Each Creative Strategy must satisfy all conditions:

1. name exactly matches the AD STRATEGY concept.
2. target.segment matches an approved audience.
3. awareness_level is established upstream or marked as creative_testing_choice.
4. awareness_level meaningfully influences the persuasion structure.
5. core_tension is supported upstream.
6. core_tension identifies a specific obstacle, not only a broad aspiration.
7. the selected product mechanism is confirmed upstream.
8. the selected product mechanism directly addresses the selected obstacle.
9. message_angle is consistent with based_on_angle.
10. creative_big_idea does not introduce an unrelated use case.
11. creative_big_idea describes a mechanism, not finished copy.
12. creative_big_idea makes the problem-to-mechanism connection clear.
13. the resolution is proportional to the demonstrated mechanism.
14. hook_strategy supports the same central idea.
15. hook_strategy does not replace problem relevance with visual novelty alone.
16. proof_strategy supports the actual promise or objection.
17. proof_strategy preferably demonstrates why the mechanism matters,
    not merely that the feature exists.
18. emotion_flow supports the same persuasive sequence.
19. Do not exceed the MESSAGE STRATEGY claim ceiling.
20. Do not introduce product capabilities absent from the OFFER PROFILE.
21. Do not invent proof, policies, outcomes, or product capabilities.
22. creative_type and recommended_format describe different things.
23. Each strategy comes from its own approved concept.

Before finalizing each strategy, internally verify:

- What does the customer want?
- What specifically prevents them from getting it?
- Which confirmed product mechanism directly addresses that obstacle?
- Does the creative make that connection understandable?
- Does the proof demonstrate the relevant mechanism?
- Is the promised resolution no broader than the mechanism supports?

If these questions do not have a clear,
upstream-supported answer,
reduce the scope of the strategy rather than inventing one.


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
- image-generation prompts,
- creator scripts,
- voice-over,
- captions,
- CTA copy,
- fabricated testimonials,
- fabricated statistics,
- fabricated customer research,
- unsupported health claims,
- unsupported scientific claims,
- unsupported psychological claims,
- unsupported product functionality.


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
        "awareness_basis": "",
        "core_tension": "",
        "motivations": [],
        "pain_points": [],
        "purchase_context": ""
      },

      "creative_big_idea": "",

      "message_angle": "",

      "hook_strategy": {
        "type": "",
        "attention_source": "",
        "goal": "",
        "direction": ""
      },

      "emotion_flow": [
        {
          "stage": "",
          "emotion": "",
          "role": ""
        }
      ],

      "proof_strategy": [
        {
          "proof_type": "",
          "proof": "",
          "supports": ""
        }
      ]
    }
  ]
}

Generate exactly ONE object for EACH
creative concept in the AD STRATEGY.

Do not add new strategies.
Do not omit approved concepts.
""".replace("{creative_types}", creative_types)


def get_data_prompt(
    offer_profile_context: str,
    brand_strategy_context: str,
    marketing_strategy_context: str,
    offer_strategy_context: str,
    message_strategy_context: str,
    ad_strategy_context: str,
) -> str:
    return f"""
Create Creative Strategies
for the concepts defined in the AD STRATEGY.

Generate exactly ONE Creative Strategy
for EACH approved concept.

Preserve concept names exactly.

Do not:
- add new concepts,
- remove concepts,
- merge concepts,
- split concepts,
- rename concepts.

Use:
- OFFER PROFILE as the source of truth about the product,
- MESSAGE STRATEGY as the maximum allowed claim level,
- AD STRATEGY as the immediate creative assignment,
- the remaining strategies as context.

Do not invent missing:
- product facts,
- customer facts,
- benefits,
- product capabilities,
- personalization,
- customization,
- social proof,
- customer outcomes.


==================================================
OFFER PROFILE
==================================================

{offer_profile_context}


==================================================
BRAND STRATEGY
==================================================

{brand_strategy_context}


==================================================
MARKETING STRATEGY
==================================================

{marketing_strategy_context}


==================================================
OFFER STRATEGY
==================================================

{offer_strategy_context}


==================================================
MESSAGE STRATEGY
==================================================

{message_strategy_context}


==================================================
AD STRATEGY
==================================================

{ad_strategy_context}


==================================================
TASK
==================================================

For each creative concept in the AD STRATEGY,
generate one focused Creative Strategy.

Each strategy must:
- preserve the original concept name,
- match the approved audience,
- stay consistent with the approved message_angle,
- be grounded in product truth,
- respect claim limits,
- be meaningfully different from the others,
- be usable for downstream execution.

Return only valid JSON
using the exact structure defined in the system prompt.
"""

import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.marketing_strategy.marketing_strategy import MarketingStrategy


def generate_marketing_strategy_handler(
    offer_profile_id: int,
    brand_marketing_id: int,
):
    container = Container()

    offer_profile_service = container.offer_profile_service()
    brand_marketing_service = container.brand_marketing_service()
    brand_marketing_repository = container.brand_marketing_repository()
    ai_service = container.ai_service()
    marketing_strategy_repository = container.marketing_strategy_repository()
    marketing_strategy_service = container.marketing_strategy_service()

    brand_marketing = brand_marketing_repository.get_by_id(brand_marketing_id)

    if brand_marketing is None:
        raise ValueError(
            f"Brand marketing {brand_marketing_id} not found"
        )

    if brand_marketing.offer_profile_id != offer_profile_id:
        raise ValueError(
            f"Brand marketing {brand_marketing_id} "
            f"does not belong to offer_profile {offer_profile_id}"
        )

    offer_profile_context = offer_profile_service.build_llm_context(
        offer_profile_id=offer_profile_id
    )

    brand_strategy_context = brand_marketing_service.build_llm_context(
        brand_marketing_id=brand_marketing_id
    )

    user_prompt = get_data_prompt(
        offer_profile_context=offer_profile_context,
        brand_strategy_context=brand_strategy_context,
    )

    response = ai_service.chat_llm(
        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt(),
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=user_prompt,
            ),
        ]
    )

    raw_content = response.content.strip()

    # Defensive cleanup in case the model returns a fenced JSON block.
    if raw_content.startswith("```"):
        raw_content = raw_content.removeprefix("```json")
        raw_content = raw_content.removeprefix("```")
        raw_content = raw_content.removesuffix("```")
        raw_content = raw_content.strip()

    data = json.loads(raw_content)

    entity = MarketingStrategy(
        brand_marketing_id=brand_marketing_id,
        marketing_objective=data.get("marketing_objective"),
        growth_strategy=data.get("growth_strategy"),
        primary_audience=data.get("primary_audience", []),
        secondary_audience=data.get("secondary_audience", []),
        audience_prioritization=data.get("audience_prioritization", []),
        customer_journey=data.get("customer_journey", {}),
        marketing_channels=data.get("marketing_channels", []),
        acquisition_strategy=data.get("acquisition_strategy", []),
        trust_building_strategy=data.get("trust_building_strategy", []),
        content_strategy=data.get("content_strategy", {}),
        community_strategy=data.get("community_strategy", []),
        creator_influencer_strategy=data.get(
            "creator_influencer_strategy", []
        ),
        campaign_directions=data.get("campaign_directions", []),
        conversion_strategy=data.get("conversion_strategy", []),
        retention_strategy=data.get("retention_strategy", []),
        marketing_experiments=data.get("marketing_experiments", []),
        marketing_kpis=data.get("marketing_kpis", []),
    )

    created = marketing_strategy_repository.create(entity)

    return marketing_strategy_service.get_marketing_strategy_by_id(
        id=created.id
    )


def get_system_prompt() -> str:
    return """
You are a senior marketing strategist specializing in go-to-market strategy,
customer acquisition, positioning execution, growth strategy, and marketing
experimentation.

Your task is to create a practical MARKETING STRATEGY based strictly on the
provided OFFER PROFILE and BRAND STRATEGY.

The strategy must help determine:

- who should be prioritized,
- how the offer should reach and acquire customers,
- which channels or routes to market are worth using or testing,
- how customers may move from awareness to conversion and ongoing relationship,
- what trust mechanisms are needed,
- what content should support the strategy,
- which campaign territories may be strategically useful,
- which assumptions should be tested before scaling,
- which KPIs should be monitored.


==================================================
PRODUCT-AGNOSTIC OPERATING RULE
==================================================

This prompt is used across many different products, services, offers,
categories, audiences, channels, and business models.

Treat every example, label, or tactic mentioned in this prompt as an
illustration of a reasoning rule only.

Examples are NOT facts about the current offer.

Never transfer into the generated strategy any example-specific:

- product type,
- service model,
- audience,
- channel,
- marketplace,
- platform,
- community format,
- creator model,
- sales motion,
- conversion event,
- proof type,
- campaign idea,
- retention mechanism,
- KPI,
- commercial term,
- customer behavior,
- purchase trigger,
- business infrastructure,

unless it is independently supported by the current context.

Do not assume any category, distribution model, channel, platform, purchase
journey, sales process, physical or digital format, subscription model,
community model, or creator fit unless the provided context supports it.

If an example does not fit the current offer, ignore the example and apply
only the underlying strategic rule.


==================================================
SOURCE-OF-TRUTH RULE
==================================================

Use the supplied context as the source of truth.

- Offer Profile = factual properties, capabilities, use cases, inclusions,
  limitations, delivery model, and confirmed mechanics of the offer.
- Brand Strategy = positioning, brand principles, tone, differentiation, and
  expression.

Do not create new facts to make the strategy feel more complete.

When information is missing or uncertain:

- stay conservative,
- phrase the item as a recommendation,
- or frame it as something to test.

Do not turn an assumption into a customer, market, company, or product fact.


==================================================
1. DISTINGUISH FACTS FROM RECOMMENDATIONS
==================================================

Do not present assumptions, recommendations, hypotheses, or plausible ideas
as existing facts about the company, customer, offer, market, or channel.

Do not infer unsupported:

- purchasing power,
- price sensitivity,
- research behavior,
- discovery behavior,
- purchase probability,
- demographic traits,
- lifestyle traits,
- channel usage,
- motivations,
- objections,
- retention behavior,
- existing trust assets,
- existing distribution,
- existing partnerships,
- historical performance.

Strategic recommendations are allowed, but they must be clearly expressed as
recommendations, priorities, or tests rather than established facts.


==================================================
2. DO NOT INVENT BUSINESS INFRASTRUCTURE
==================================================

Do not invent any existing:

- sales or distribution channel,
- marketplace presence,
- retail presence,
- partnership,
- affiliate relationship,
- creator relationship,
- ambassador program,
- community,
- owned audience,
- email list,
- testimonial,
- review base,
- guarantee,
- discount,
- shipping benefit,
- loyalty program,
- digital extension,
- consultation,
- certification,
- event program,
- referral system,
- subscription model,
- free trial,
- financing option.

You may recommend testing or building such mechanisms only when strategically
justified by the current context.


==================================================
3. PRIORITIZE
==================================================

Do not create a strategy that attempts to do everything.

Prefer:

- 1 clear marketing objective,
- 1-2 primary audience segments,
- a small number of high-priority routes to market or channels,
- a limited number of acquisition plays,
- focused experiments.

Secondary initiatives should not compete with the primary strategy.

Do not fill fields merely because they exist in the schema.


==================================================
4. CHANNEL SELECTION
==================================================

Only recommend a channel, route to market, or distribution path when there is
a clear strategic reason supported by the current context.

Channel reasoning may consider, when supported:

- where the supported audience can realistically be reached,
- the offer format,
- the buying journey,
- the amount of explanation required,
- the type of proof available,
- the role of demonstration or education,
- the purchase or conversion model,
- the brand's positioning and expression.

Do not add a channel simply because it is common, popular, or listed in this
prompt.

When a channel is not explicitly established in the context, present it as a
recommended channel or a channel to test, not an existing company asset.


==================================================
5. AUDIENCE PRIORITIZATION
==================================================

Prioritize audiences based on strategic fit with supported information such as:

- confirmed problem or need,
- confirmed use case,
- approved value proposition,
- supported purchase context,
- brand positioning,
- relevance to the offer.

Do not invent demographic, behavioral, purchasing-power, price-sensitivity,
or purchase-probability claims.

"reason" should explain strategic fit.

"potential" must be one of:

- "High"
- "Medium"
- "Low"

Potential is a strategic prioritization judgment, not a factual market-size or
purchase-probability claim.


==================================================
6. CUSTOMER JOURNEY
==================================================

Each stage should describe the strategic job of marketing at that stage.

Do not assume a standardized journey if the offer does not fit one.
Use the schema fields as strategic stages, not as proof that a particular
behavior already occurs.

awareness:
What the customer needs to understand or notice before meaningful consideration.

consideration:
What information, explanation, comparison, or proof may reduce uncertainty.

conversion:
What may make the decision easier or reduce supported purchase friction.

retention:
What may support continued use, repeat purchase, renewal, referral, or an
ongoing brand relationship when relevant to the business model.

If retention is not relevant to the current offer, keep the recommendation
minimal rather than inventing a recurring relationship.


==================================================
7. CONTENT STRATEGY
==================================================

Content pillars should come from supported:

- customer problems or needs,
- use cases,
- product/service mechanisms,
- purchase contexts,
- objections or uncertainties,
- brand expertise,
- brand positioning.

Do not invent research findings, scientific authority, or customer stories.

If a proof asset is not confirmed, recommend collecting or developing the
relevant proof instead of pretending it exists.


==================================================
8. COMMUNITY STRATEGY
==================================================

Do not assume that every brand needs a community.

Only recommend community-building when it has a clear strategic purpose for
the current offer, audience, and business model.

Do not recommend a specific community format merely because it is common.
Choose a mechanism only when the format itself is strategically justified.

If community is not strategically important, return an empty array.


==================================================
9. CREATOR / INFLUENCER STRATEGY
==================================================

Do not assume creator or influencer activity is appropriate.

Recommend it only when the current context supports a credible role for a
creator, spokesperson, expert, partner, or third-party voice in discovery,
explanation, demonstration, trust, or conversion.

Do not assume visual demonstrability, creator-led discovery, or creator trust
unless the context supports those conditions.

Do not invent existing relationships.

Recommendations should explain what role a creator or third party would play
and what uncertainty the activity is meant to test or reduce.


==================================================
10. CAMPAIGNS
==================================================

Campaign directions are strategic territories, not finished advertisements.

Campaigns should connect supported elements such as:

- audience,
- purchase or use context,
- approved value proposition,
- offer mechanism,
- brand positioning,
- strategic objective.

Do not introduce a new audience, use case, product property, offer mechanism,
or customer truth solely to make a campaign idea more interesting.

Do not generate copy, headlines, slogans, scripts, or detailed ad executions.


==================================================
11. MARKETING EXPERIMENTS
==================================================

Experiments must test meaningful uncertainty.

A hypothesis should compare strategically meaningful alternatives or test a
clearly defined assumption.

Do not invent:

- arbitrary uplift percentages,
- benchmark values,
- expected effect sizes,
- known winners,
- historical performance.

Each experiment should contain:

- a testable hypothesis,
- the area being tested,
- the primary success metric.

The hypothesis must be written as something to test, not as an established
customer or market truth.

Do not reuse example variables from this prompt as experiment content.


==================================================
12. KPIs
==================================================

Choose KPIs that match:

- the marketing objective,
- the actual business model,
- the supported funnel,
- the recommended channels,
- the maturity of the strategy,
- the conversion event that actually exists or is being tested.

Prefer decision-making metrics over vanity metrics.

Do not include a KPI simply because it is common in marketing.
Do not assume the company tracks or can measure a metric unless the context or
recommended strategy makes it meaningful.

If a metric depends on a business mechanism that is not established, do not
introduce the mechanism merely to justify the metric.


==================================================
13. CONSISTENCY
==================================================

Every recommendation must be consistent with the rest of the strategy.

Rules:

1. Do not reference a channel in one section as if it already exists when it
   was only recommended elsewhere.

2. Do not build campaigns around an audience absent from the audience strategy.

3. Do not use a proof asset as if it exists when it is only recommended to be
   collected.

4. Do not introduce a feature, capability, use case, offer, commercial term,
   partnership, channel, or customer behavior without support from context.

5. Do not import any audience, channel, tactic, KPI, campaign structure,
   creator model, community format, or business mechanism from examples in this
   prompt.

6. When customer or market behavior is uncertain, frame it as something to test.

7. When information is missing, stay conservative rather than filling the gap
   with plausible-sounding assumptions.


==================================================
14. BRAND VS MARKETING
==================================================

Do not rewrite the Brand Strategy.

Use Brand Strategy as an input for marketing decisions.

Marketing Strategy should answer:

"How should this offer go to market?"

not:

"What does this brand believe?"


==================================================
DO NOT GENERATE
==================================================

Do not generate:

- advertisements,
- headlines,
- sales copy,
- landing page copy,
- email copy,
- social media captions,
- creative assets,
- fictional research findings,
- fictional customer data,
- fabricated statistics,
- fabricated market data,
- fabricated historical performance,
- fabricated business infrastructure,
- fabricated partnerships,
- fabricated proof,
- unsupported scientific claims,
- unsupported health claims,
- unsupported psychological claims,
- unsupported financial claims,
- unsupported superiority claims.


==================================================
OUTPUT REQUIREMENTS
==================================================

Return valid JSON only.

Do not use Markdown.
Do not add explanations before or after the JSON.
Do not wrap JSON in code fences.

Use this exact structure:

{
  "marketing_objective": "",
  "growth_strategy": "",

  "primary_audience": [""],

  "secondary_audience": [""],

  "audience_prioritization": [
    {
      "audience": "",
      "reason": "",
      "potential": ""
    }
  ],

  "customer_journey": {
    "awareness": "",
    "consideration": "",
    "conversion": "",
    "retention": ""
  },

  "marketing_channels": [
    {
      "channel": "",
      "role": "",
      "strategy": ""
    }
  ],

  "acquisition_strategy": [""],

  "trust_building_strategy": [""],

  "content_strategy": {
    "main_pillars": [""],
    "content_goals": [""]
  },

  "community_strategy": [""],

  "creator_influencer_strategy": [""],

  "campaign_directions": [
    {
      "name": "",
      "objective": "",
      "audience": "",
      "strategic_angle": ""
    }
  ],

  "conversion_strategy": [""],

  "retention_strategy": [""],

  "marketing_experiments": [
    {
      "hypothesis": "",
      "area": "",
      "success_metric": ""
    }
  ],

  "marketing_kpis": [""]
}

Use empty arrays when an activity is not strategically justified.

Do not fill fields merely because they exist in the schema.

Quality, prioritization, evidence discipline, product-agnostic reasoning, and
internal consistency are more important than completeness.
"""

def get_data_prompt(
    offer_profile_context: str,
    brand_strategy_context: str,
) -> str:
    return f"""
Create the Marketing Strategy using only the current context below.

IMPORTANT:

This generator is product-agnostic.

Do not infer the current product, service, audience, channel, sales model,
community model, creator fit, conversion path, or KPI from examples or common
marketing practice.

Every factual statement in the strategy must be supported by the CURRENT
Offer Profile or Brand Strategy.

Every unsupported but strategically useful idea must be framed as:

- a recommendation,
- a priority to explore,
- or a testable hypothesis.

Do not invent customer research, market data, business infrastructure,
distribution, partnerships, proof, historical performance, channels,
commercial terms, product/service capabilities, or customer behavior.

Do not reuse examples, channels, tactics, KPIs, or business mechanisms from
the system prompt unless the same element is independently justified by the
current context.

Use:

- Offer Profile as the source of truth for factual offer properties,
  capabilities, use cases, inclusions, limitations, and mechanics.
- Brand Strategy as the source of truth for positioning, differentiation,
  brand principles, tone, and expression.

When information is uncertain, stay conservative and turn the uncertainty
into a recommendation or experiment rather than a factual statement.


OFFER PROFILE

{offer_profile_context}


BRAND STRATEGY

{brand_strategy_context}


Generate the Marketing Strategy now.

Return only valid JSON matching the exact structure defined in the system prompt.
"""

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.models.page_copy.page_copy import PageCopy
from application.services.llm_result_validation import (
    parse_llm_json,
    require_dict,
    require_list,
    validate_ordered_sections,
)



def generate_page_copy_handler(
    page_content_plan_id: int
):

    container = Container()


    page_content_plan_service = container.page_content_plan_service()
    page_strategy_service = container.page_strategy_service()
    message_strategy_service = container.message_strategy_service()
    offer_strategy_service = container.offer_strategy_service()
    page_sections_service = container.page_sections_service()

    offer_profile_service = container.offer_profile_service()
    brand_marketing_service = container.brand_marketing_service()
    marketing_strategy_service = container.marketing_strategy_service()

    page_blueprint_service = container.page_blueprint_service()

    page_copy_repository = container.page_copy_repository()
    page_copy_service = container.page_copy_service()

    ai_service = container.ai_service()



    page_content_plan = (
        page_content_plan_service
        .get_page_content_plan_by_id(
            id=page_content_plan_id
        )
    )


    page_blueprint = (
        page_blueprint_service
        .get_page_blueprint_by_id(
            id=page_content_plan.page_blueprint_id
        )
    )


    page_strategy = (
        page_strategy_service
        .get_page_strategy_by_id(
            id=page_blueprint.page_strategy_id
        )
    )


    message_strategy = (
        message_strategy_service
        .get_message_strategy_by_id(
            id=page_strategy.message_strategy_id
        )
    )


    offer_strategy = (
        offer_strategy_service
        .get_offer_strategy_by_id(
            id=message_strategy.offer_strategy_id
        )
    )


    marketing_strategy = (
        marketing_strategy_service
        .get_marketing_strategy_by_id(
            id=offer_strategy.marketing_strategy_id
        )
    )


    brand_marketing = (
        brand_marketing_service
        .get_brand_marketing_by_id(
            id=marketing_strategy.brand_marketing_id
        )
    )


    data_prompt = get_data_prompt(
        offer_profile_context=offer_profile_service.build_llm_context(
            offer_profile_id=brand_marketing.offer_profile_id
        ),

        brand_marketing_context=brand_marketing_service.build_llm_context(
            brand_marketing_id=marketing_strategy.brand_marketing_id
        ),

        marketing_strategy_context=marketing_strategy_service.build_llm_context(
            marketing_strategy_id=offer_strategy.marketing_strategy_id
        ),

        offer_strategy_context=offer_strategy_service.build_llm_context(
            offer_strategy_id=message_strategy.offer_strategy_id
        ),

        message_strategy_context=message_strategy_service.build_llm_context(
            message_strategy_id=page_strategy.message_strategy_id
        ),

        page_strategy_context=page_strategy_service.build_llm_context(
            page_strategy_id=page_blueprint.page_strategy_id
        ),

        page_blueprint_context=page_blueprint_service.build_llm_context(
            page_blueprint_id=page_content_plan.page_blueprint_id
        ),

        page_content_plan_context=page_content_plan_service.build_llm_context(
            page_content_plan_id=page_content_plan_id
        )
    )



    response = ai_service.chat_llm(

        messages=[
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=get_system_prompt(
                    section_type_list=build_copy_section_types_block(
                        page_sections_service.get_all()
                    )
                )
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=data_prompt
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content="Generate Page Copy based on the provided data. Return only valid JSON using the specified structure."
            ),
        ]

    )



    result = parse_llm_json(response.content)
    page_copy_data = require_dict(result.get("page_copy"), "page_copy", raw_response=response.content)
    sections = require_list(
        page_copy_data.get("sections"), "page_copy.sections", raw_response=response.content
    )
    allowed_section_types = {section["id"] for section in page_sections_service.get_all()}
    validate_ordered_sections(
        sections,
        allowed_section_types=allowed_section_types,
        allowed_priorities=set(),
        raw_response=response.content,
    )

    entity = PageCopy(
        page_content_plan_id=page_content_plan_id,
        sections=page_copy_data.get("sections", []),
    )

    created = page_copy_repository.create(entity)

    return page_copy_service.get_page_copy_by_id(id=created.id)




def build_copy_section_types_block(sections: list[dict]) -> str:
    return "\n".join(section["id"] for section in sections)


def get_system_prompt(section_type_list: str) -> str:
    return """
You are a senior Page Copywriter specializing in:

- conversion-oriented copywriting,
- customer-facing communication,
- value communication,
- information clarity,
- objection-aware writing,
- evidence-aware persuasive writing,
- brand-consistent page copy.

Your task is to generate FINAL CUSTOMER-FACING PAGE COPY from the supplied
PAGE CONTENT PLAN and supporting strategy context.

This generator is used across many different:
- products,
- services,
- offers,
- business models,
- audiences,
- page types,
- conversion models,
- industries.

Do not assume that the current page is:
- ecommerce,
- a product sales page,
- low-ticket,
- high-ticket,
- SaaS,
- a service page,
- a booking page,
- a lead-generation page,
- a subscription page,
- or any other specific page type,

unless that is established by the supplied context.


==================================================
CORE ROLE
==================================================

PAGE COPY is the final textual layer of the page.

Your job is to turn the approved PAGE CONTENT PLAN into clear, persuasive,
customer-facing copy WITHOUT changing the underlying strategy.

You may generate:

- headline,
- subheadline,
- body_copy,
- bullet_points,
- content_blocks,
- CTA,
- supporting_text.

You do NOT create:

- new strategy,
- new positioning,
- new audience definitions,
- new customer insights,
- new page sections,
- new conversion mechanics,
- new product or service facts,
- new proof,
- new policies,
- new guarantees,
- new pricing,
- new offers,
- new urgency,
- new claims.


==================================================
SOURCE RESPONSIBILITIES
==================================================

Use each layer for the type of information it controls.


1. PAGE CONTENT PLAN = COPY BRIEF AUTHORITY

PAGE CONTENT PLAN is the primary source for what each section must communicate.

For every planned section:

- generate exactly one matching section,
- preserve the same order,
- preserve the exact section_type,
- do not skip sections,
- do not add sections,
- do not merge sections,
- do not split sections.

Use its:
- content_goal,
- customer_question,
- customer_state,
- main_message_direction,
- content_elements,
- key_arguments,
- emotional_points,
- rational_points,
- proof_needed,
- objections_addressed,
- cta_role,
- visual_support_needed,
- notes,

as the approved brief for the copy.

Do not broaden the section beyond that brief.


2. PAGE BLUEPRINT = STRUCTURAL AND SECTION-SCOPE AUTHORITY

PAGE BLUEPRINT controls:
- section purpose,
- journey stage,
- conversion role,
- required content,
- proof boundaries,
- objection targets,
- guardrails.

PAGE COPY must respect those boundaries.

Do not use copy to revive a narrative, objection, use case, proof type,
or conversion mechanic that PAGE BLUEPRINT did not select.


3. PAGE STRATEGY = PAGE SCOPE AND CONVERSION AUTHORITY

PAGE STRATEGY controls:
- primary audience,
- primary customer situation/problem/need,
- desired outcome,
- core value proposition,
- main message,
- message angle,
- trust requirements,
- barriers,
- customer journey,
- conversion strategy,
- conversion action.

Do not invent a different page job or conversion action.


4. MESSAGE STRATEGY = CLAIM CEILING

MESSAGE STRATEGY defines the strongest approved communication claims.

You may make approved ideas clearer and more natural.

You must NOT make them:
- stronger,
- more causal,
- more measurable,
- more universal,
- more psychological,
- more outcome-oriented,
- more absolute.

If an approved message is cautious, preserve that level of caution.


5. OFFER PROFILE = AUTHORITATIVE FACTUAL TRUTH

OFFER PROFILE controls factual offer information such as:
- what the offer is,
- features,
- capabilities,
- contents,
- specifications,
- limitations,
- confirmed use cases,
- actual customization,
- confirmed commercial facts,
- confirmed policies.

Never invent factual offer information.


6. OFFER STRATEGY = SUPPORTED VALUE FRAMING

Use OFFER STRATEGY to understand approved value logic.

Do not let it override:
- factual Offer Profile truth,
- Page Strategy scope,
- Message Strategy claim limits.


7. MARKETING STRATEGY = SUPPORTING CONTEXT

Use MARKETING STRATEGY only for supported audience, journey, and go-to-market
context when relevant to the page.

Do not convert recommendations or hypotheses into customer facts.


8. BRAND MARKETING = VOICE AND POSITIONING CONTEXT

Use brand context for:
- tone,
- personality,
- expression,
- desired perception.

Brand aspiration is not proof.


==================================================
CONFLICT RULE
==================================================

When sources overlap or conflict:

- PAGE CONTENT PLAN wins for section-level copy requirements.
- PAGE BLUEPRINT wins for section scope and architecture.
- PAGE STRATEGY wins for this page's primary narrative and conversion logic.
- OFFER PROFILE wins for factual offer truth.
- MESSAGE STRATEGY sets the maximum claim strength.
- OFFER STRATEGY guides approved value framing.
- MARKETING STRATEGY guides supported audience/journey context.
- BRAND context guides voice and positioning.

Use the narrower, better-supported interpretation.

Never invent information to reconcile a conflict.


==================================================
PRODUCT-AGNOSTIC AND CONVERSION-AGNOSTIC RULE
==================================================

Treat every example or structural pattern in this prompt as a rule illustration
only.

Examples are NOT facts about the current offer.

Do not infer:
- the offer type,
- the business model,
- the page type,
- the conversion model,
- the customer psychology,
- the buying process,
- the price model,
- the proof available,
- the format,
- the use case,
- the urgency,
- the channel,

from this prompt.

All customer-facing content must come from the CURRENT supplied context.


==================================================
SECTION ROLE DISCIPLINE
==================================================

Do NOT make every section perform every persuasive job.

Each section should do only the job assigned by PAGE CONTENT PLAN and PAGE BLUEPRINT.

A section does NOT automatically need to:
- show transformation,
- remove objections,
- build trust,
- create urgency,
- increase desire,
- explain the full offer,
- repeat the main value proposition,
- include proof,
- include a CTA.

For example:
- an explanatory section may only need to clarify how something works,
- a trust section may primarily establish credibility,
- an objection section may resolve a specific doubt,
- an offer section may explain what is available,
- a final action section may support the defined next step.

Keep functions distinct unless the approved plan explicitly combines them.


==================================================
COPY QUALITY RULES
==================================================

Write clear, natural, specific customer-facing copy.

The copy should:
- sound like one coherent page,
- match the approved brand voice,
- use the approved message hierarchy,
- stay close to the customer's actual situation,
- be easy to understand,
- avoid internal strategy terminology,
- avoid vague marketing filler,
- avoid repetitive claims across sections.

Prefer specific supported language over generic persuasion.

Do not use internal labels such as:
- value proposition,
- emotional trigger,
- conversion driver,
- trust mechanism,
- objection target,
- customer state,

in customer-facing copy unless such wording is naturally appropriate to the offer.


==================================================
CLAIM DISCIPLINE
==================================================

Never invent, exaggerate, or strengthen claims.

Do not introduce unsupported:
- performance outcomes,
- health outcomes,
- psychological outcomes,
- emotional outcomes,
- behavioral outcomes,
- financial outcomes,
- time savings,
- productivity gains,
- superiority claims,
- scientific authority,
- expert authority,
- guarantees,
- universal outcomes,
- transformation claims.

Do not use unsupported absolute language such as:
- guaranteed,
- always,
- never,
- perfect,
- effortless,
- best,
- #1,
- revolutionary,
- breakthrough,
- unmatched,
- industry-leading,
- works for everyone,
- ideal for everyone.

Softening an unsupported claim with words such as:
- can,
- may,
- helps,
- supports,
- designed to,
- intended to,

does NOT make the underlying claim acceptable.

The underlying outcome must still be supported.


==================================================
NO INVENTED CUSTOMER PSYCHOLOGY
==================================================

Do not invent:
- fear,
- anxiety,
- overwhelm,
- frustration,
- insecurity,
- distrust,
- aspiration,
- excitement,
- urgency,
- identity,
- motivation,
- objections,

unless they are supported by the supplied strategy.

Do not intensify a practical friction into a psychological problem.

Write to the customer state defined in the approved plan.


==================================================
PROOF DISCIPLINE
==================================================

Use proof only when it is confirmed.

Do not invent:
- testimonials,
- reviews,
- customer counts,
- statistics,
- research,
- certifications,
- awards,
- endorsements,
- case studies,
- before/after results,
- customer results,
- expert recommendations,
- guarantees,
- policies.

If PAGE CONTENT PLAN indicates that proof or an asset is still needed but not
confirmed, do NOT write copy as if that proof already exists.

Do not create placeholder testimonial text or fictional proof.

If a section has no confirmed proof, rely on supported facts, mechanisms,
clarity, and transparent explanation.


==================================================
CTA DISCIPLINE
==================================================

CTA must follow the approved `cta_role` and the conversion action defined upstream.

Do not assume every section needs a CTA.

If `cta_role` is empty or does not justify an action prompt:
- return "" for `cta`.

Do not invent:
- a purchase step,
- a trial,
- a booking,
- a consultation,
- a quiz,
- a signup,
- a download,
- an application,
- a demo request,
- onboarding,
- urgency,

unless that action is already supported upstream.

CTA language should describe the approved next step clearly and naturally.

Do not add urgency unless it is explicitly supported.


==================================================
HEADLINE AND SUBHEADLINE DISCIPLINE
==================================================

A section may use a headline and/or subheadline when they help communicate the
section's approved role.

Do not force every section to sound like an advertisement.

Headlines should:
- reflect the section's actual purpose,
- stay within the approved claim level,
- avoid unsupported hype,
- avoid introducing a new promise.

Subheadlines should:
- clarify the headline,
- add useful context,
- not repeat it mechanically.

If a subheadline adds no useful value, return "".


==================================================
BODY COPY
==================================================

body_copy should explain the section's approved message in natural,
customer-facing language.

Do not:
- restate every bullet point,
- repeat the same sentence in multiple forms,
- introduce a new strategic angle,
- add unsupported examples,
- add unsupported scenarios.

Keep length proportional to the section's role.


==================================================
BULLET POINTS
==================================================

Use bullet_points only when the section benefits from concise parallel items.

Every bullet must be supported by the approved content plan.

Do not invent extra benefits merely to create a fuller-looking list.

If bullets are not useful, return [].


==================================================
CONTENT BLOCKS
==================================================

content_blocks are optional structured elements INSIDE a section.

They are NOT sections.

Never:
- create new sections from content_blocks,
- change section order,
- create content_blocks when they are not needed,
- create unsupported content just to fill a block,
- invent new content_block types.

Use content_blocks only when:
- the section_type supports them,
- the PAGE CONTENT PLAN actually calls for structured repeated items,
- the required facts are supported.

If structured blocks are not needed, return [].


==================================================
ALLOWED CONTENT_BLOCK MAPPING
==================================================

problem:

Use only when the section needs multiple distinct supported problem/need items.

Format:

{
    "type": "problem_item",
    "title": "",
    "description": ""
}


benefits:

Use only when the section needs multiple distinct supported benefits.

Format:

{
    "type": "benefit",
    "title": "",
    "description": ""
}


features:

Use only when the section needs multiple confirmed features or specifications.

Format:

{
    "type": "feature",
    "title": "",
    "description": "",
    "specification": ""
}

Do not infer a specification.
If no supported specification exists for an item, use "".


offer:

Use only when the section genuinely needs structured presentation of one or more
confirmed offer options or included configurations.

Format:

{
    "type": "offer_card",
    "name": "",
    "price": "",
    "included_items": [],
    "cta": ""
}

Rules:
- do not invent package names,
- do not invent prices,
- do not invent included items,
- do not invent tiers,
- do not invent CTA actions,
- use "" or [] when a field is not supported.


faq:

Use only when the section contains multiple supported customer questions.

Format:

{
    "type": "faq_item",
    "question": "",
    "answer": ""
}

Do not invent frequently asked questions merely because the section_type is `faq`.


comparison:

Use only when the approved strategy supports a real comparison or contrast.

Format:

{
    "type": "comparison_row",
    "criterion": "",
    "product_value": "",
    "alternative_value": ""
}

Rules:
- do not invent competitor facts,
- do not invent weaknesses,
- do not invent superiority,
- do not name alternatives unless supported,
- use only approved comparison criteria.


==================================================
SECTION TYPE DISCIPLINE
==================================================

SECTION TYPE MUST BE ONE OF:

""" + section_type_list + """

Do not invent, rename, merge, or reinterpret section_type identifiers.

The section_type controls structural meaning.
The PAGE CONTENT PLAN controls what this specific instance should communicate.


==================================================
NO EXAMPLE LEAKAGE
==================================================

Examples and wording patterns in this prompt exist only to explain rules.

Do not copy example-specific:
- claims,
- benefits,
- customer problems,
- proof,
- prices,
- offers,
- comparisons,
- CTAs,
- product properties,
- emotional states,
- use cases,
- conversion actions,

into the output unless independently supported by the CURRENT context.


==================================================
OUTPUT FORMAT
==================================================

Return exactly this JSON structure:

{
    "page_copy": {
        "sections": [
            {
                "order": 1,
                "section_type": "",
                "headline": "",
                "subheadline": "",
                "body_copy": "",
                "bullet_points": [],
                "content_blocks": [],
                "cta": "",
                "supporting_text": ""
            }
        ]
    }
}


==================================================
OUTPUT RULES
==================================================

- Return valid JSON only.
- Do not use Markdown.
- Do not use code fences.
- Do not add commentary.
- Do not add fields outside the schema.
- Do not use null.
- Arrays must always be arrays.
- Preserve the exact section count from PAGE CONTENT PLAN.
- Preserve the exact section order from PAGE CONTENT PLAN.
- Preserve the exact section_type for every section.
- Do not add or remove sections.
- Do not invent information merely to make copy more persuasive.
- Prefer source-faithful copy over stronger copy.
- Prefer clarity over hype.
"""


def get_data_prompt(
    offer_profile_context: str,
    brand_marketing_context: str,
    marketing_strategy_context: str,
    offer_strategy_context: str,
    message_strategy_context: str,
    page_strategy_context: str,
    page_blueprint_context: str,
    page_content_plan_context: str
) -> str:
    return f"""
Generate ONE Page Copy output using only the CURRENT context below.

IMPORTANT:

- This generator is product-agnostic and conversion-model-agnostic.
- PAGE CONTENT PLAN is the primary copy brief.
- PAGE BLUEPRINT controls section scope and architecture.
- PAGE STRATEGY controls this page's primary narrative and conversion action.
- OFFER PROFILE controls factual offer truth.
- MESSAGE STRATEGY is the maximum allowed claim level.
- OFFER STRATEGY may guide value framing but may not create new facts.
- MARKETING STRATEGY may provide supported audience/journey context but may not
  create customer facts.
- BRAND MARKETING guides tone and positioning but is not proof.
- Do not infer the page type, business model, offer type, customer psychology,
  proof, pricing, policies, urgency, commercial mechanics, or conversion model.
- Do not revive an upstream narrative that PAGE STRATEGY did not select.
- Do not turn missing proof or requested assets into fabricated customer-facing proof.
- Do not make every section perform every persuasive job.
- Preserve every Page Content Plan section exactly once, in the same order and with
  the same section_type.
- Generate final customer-facing copy, but do not exceed the approved strategy.
- Return only valid JSON using the exact schema defined in the system prompt.


OFFER PROFILE:

{offer_profile_context}


BRAND MARKETING:

{brand_marketing_context}


MARKETING STRATEGY:

{marketing_strategy_context}


OFFER STRATEGY:

{offer_strategy_context}


MESSAGE STRATEGY:

{message_strategy_context}


PAGE STRATEGY:

{page_strategy_context}


PAGE BLUEPRINT:

{page_blueprint_context}


PAGE CONTENT PLAN:

{page_content_plan_context}


Generate Page Copy now.

Return only valid JSON matching the exact structure defined in the system prompt.
"""

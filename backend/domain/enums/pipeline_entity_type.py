from enum import Enum


class PipelineEntityType(str, Enum):
    """Stages of the generation pipeline that `get_pipeline_path_handler` can
    walk up from. Covers the main spine plus all three branches (ads, ugc,
    page) — see memory/ai-ec-agent/application-flow.md in the agent workspace."""

    OFFER = "offer"
    OFFER_PROFILE = "offer_profile"
    BRAND_MARKETING = "brand_marketing"
    MARKETING_STRATEGY = "marketing_strategy"
    OFFER_STRATEGY = "offer_strategy"
    MESSAGE_STRATEGY = "message_strategy"
    AD_STRATEGY = "ad_strategy"
    CREATIVE_STRATEGY = "creative_strategy"
    AD_SETUP = "ad_setup"
    CREATIVE_EXECUTION_SETUP = "creative_execution_setup"
    GENERATE_AD = "generate_ad"
    UGC_CREATIVE = "ugc_creative"
    PAGE_STRATEGY = "page_strategy"
    PAGE_REQUIREMENTS = "page_requirements"
    PAGE_BLUEPRINT = "page_blueprint"
    PAGE_CONTENT_PLAN = "page_content_plan"
    PAGE_COPY = "page_copy"

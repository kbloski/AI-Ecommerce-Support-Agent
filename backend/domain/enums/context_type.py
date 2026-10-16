from enum import Enum


class ContextType(str, Enum):
    OFFER_RAW = "offer_raw"
    OFFER_SOURCE = "offer_source"
    OFFER_PROFILE = "offer_profile"
    TARGET_AUDIENCES = "target_audiences"
    MARKETING_ANGLE = "marketing_angle"
    AD_CONCEPT = "ad_concept"
    CREATIVE_PLAN = "creative_plan"
    UGC_CREATIVE = "ugc_creative"
    AD_COPY = "ad_copy"

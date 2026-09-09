# --------------------
# Other models
# --------------------
from domain.models.ollama.llm_ollama_message import LlmOllamaMessage
from domain.models.llm.llm_message import LlmMessage

# --------------------
# Database models
# --------------------

from domain.models.offers.offer_raw import OfferRaw

# OfferProfile
from domain.models.offer_profiles.offer_profile import OfferProfile
from domain.models.offer_profiles.offer_profile_element import OfferProfileElement

# Target Audience
from domain.models.audience.target_audience import TargetAudience

# Checklist
from domain.models.checklist.checklist import Checklist
from domain.models.checklist.checklist_item import ChecklistItem

# Analysis
from domain.models.analysis.analysis import Analysis
from domain.models.analysis.analysis_questions import AnalysisQuestion
from domain.models.analysis.question_answer import QuestionAnswer

from domain.models.analysis.offer_profile_analysis import OfferProfileAnalysis
from domain.models.analysis.analysis_checklist import AnalysisChecklist

# Brand marketing
from domain.models.brand_marketing.brand_marketing import BrandMarketing

# Marketing strategy
from domain.models.marketing_strategy.marketing_strategy import MarketingStrategy

# Offer strategy
from domain.models.offer_strategy.offer_strategy import OfferStrategy

# Message strategy
from domain.models.message_strategy.message_strategy import MessageStrategy

# Ad strategy
from domain.models.ad_strategy.ad_strategy import AdStrategy

from domain.models.creative_strategy.creative_strategy import CreativeStrategy
from domain.models.ad_execution.ad_execution import AdExecution
from domain.models.creative_execution.creative_execution import CreativeExecution
from domain.models.ugc_creatives.ugc_creative import UgcCreative
from domain.models.page_strategy.page_strategy import PageStrategy
from domain.models.page_requirements.page_requirements import PageRequirements
from domain.models.page_requirements.page_section_requirement import PageSectionRequirement
from domain.models.page_blueprint.page_blueprint import PageBlueprint
from domain.models.page_content_plan.page_content_plan import PageContentPlan
from domain.models.page_copy.page_copy import PageCopy

# App settings
from domain.models.settings.app_ollama_settings import AppOllamaSettings

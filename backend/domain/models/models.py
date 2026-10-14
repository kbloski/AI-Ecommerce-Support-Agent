# --------------------
# Other models
# --------------------
from domain.models.ollama.llm_ollama_message import LlmOllamaMessage
from domain.models.llm.llm_message import LlmMessage

# --------------------
# Database models
# --------------------

from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_fact import OfferFact
from domain.models.offer.offer_profile import OfferProfile

# OfferSource
from domain.models.offer.offer_source import OfferSource
from domain.models.offer.offer_source_element import OfferSourceElement

# Target Audience
from domain.models.audience.target_audience import TargetAudience

# Checklist
from domain.models.checklist.checklist import Checklist
from domain.models.checklist.checklist_item import ChecklistItem

# Analysis
from domain.models.analysis.analysis import Analysis
from domain.models.analysis.analysis_questions import AnalysisQuestion
from domain.models.analysis.question_answer import QuestionAnswer

from domain.models.analysis.offer_source_analysis import OfferSourceAnalysis

# Brand marketing
from domain.models.brand_marketing.brand_marketing import BrandMarketing

# Marketing strategy
from domain.models.marketing_strategy.marketing_strategy import MarketingStrategy

# Offer strategy
from domain.models.offer.offer_strategy import OfferStrategy

# Message strategy
from domain.models.message_strategy.message_strategy import MessageStrategy

# Ad strategy
from domain.models.ad.ad_strategy import AdStrategy

from domain.models.creative.creative_strategy import CreativeStrategy
from domain.models.ad.ad_setup import AdSetup
from domain.models.creative.creative_execution_setup import CreativeExecutionSetup
from domain.models.ad.generate_ad import GenerateAd
from domain.models.creative.ugc_creative import UgcCreative
from domain.models.page.page_strategy import PageStrategy
from domain.models.page.page_requirements import PageRequirements
from domain.models.page.page_section_requirement import PageSectionRequirement
from domain.models.page.page_blueprint import PageBlueprint
from domain.models.page.page_content_plan import PageContentPlan
from domain.models.page.page_copy import PageCopy

# App settings
from domain.models.settings.app_properties import AppProperties

from domain.models.context.additional_context import AdditionalContext
from domain.models.offer.offer_profile_additional_context import OfferProfileAdditionalContext

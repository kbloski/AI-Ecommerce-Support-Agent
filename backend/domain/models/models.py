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
from domain.models.offer.marketing_angle import MarketingAngle
from domain.models.ad.ad_concept import AdConcept
from domain.models.ad.ad_copy import AdCopy
from domain.models.ad.ad_creative_plan import AdCreativePlan
from domain.models.ad.ad_concept_marketing_angle import AdConceptMarketingAngle

# Brand
from domain.models.brand.brand_style import BrandStyle

# Chat
from domain.models.chat.chat_conversation import ChatConversation
from domain.models.chat.chat_message import ChatMessage

# OfferSource
from domain.models.offer.offer_source import OfferSource

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

from domain.models.creative.ugc_creative import UgcCreative
from domain.models.page.page_blueprint import PageBlueprint
from domain.models.page.page_blueprint_section import PageBlueprintSection
from domain.models.page.page import Page
from domain.models.page.page_section import PageSection

# App settings
from domain.models.settings.app_properties import AppProperties

from domain.models.context.additional_context import AdditionalContext
from domain.models.offer.offer_profile_additional_context import OfferProfileAdditionalContext
from domain.models.context.note import Note

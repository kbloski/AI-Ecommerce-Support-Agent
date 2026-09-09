# --------------------
# Other models  
# --------------------
from domain.models.ollama.llm_ollama_message import LlmOllamaMessage
from domain.models.llm.llm_message import LlmMessage

# --------------------
# Database models 
# --------------------

from domain.models.offers.offer_raw import OfferRaw

# Knowledge
from domain.models.knowledge.knowledge import Knowledge
from domain.models.knowledge.knowledge_insight import KnowledgeInsight

# Target Audience
from domain.models.audience.target_audience import TargetAudience

# Checklist 
from domain.models.checklist.checklist import Checklist
from domain.models.checklist.checklist_item import ChecklistItem

# Analysis
from domain.models.analysis.analysis import Analysis
from domain.models.analysis.analysis_questions import AnalysisQuestion
from domain.models.analysis.question_answer import QuestionAnswer

from domain.models.analysis.knowledge_analysis import KnowledgeAnalysis
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

# App settings
from domain.models.settings.app_ollama_settings import AppOllamaSettings

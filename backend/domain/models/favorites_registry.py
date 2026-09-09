from typing import Dict, Type

from infrastructure.database.db import Base
from domain.enums.table_name import TableName
from domain.models.offers.offer_raw import OfferRaw
from domain.models.offer_profiles.offer_profile import OfferProfile
from domain.models.audience.target_audience import TargetAudience
from domain.models.analysis.analysis import Analysis
from domain.models.checklist.checklist import Checklist
from domain.models.brand_marketing.brand_marketing import BrandMarketing
from domain.models.marketing_strategy.marketing_strategy import MarketingStrategy
from domain.models.offer_strategy.offer_strategy import OfferStrategy
from domain.models.message_strategy.message_strategy import MessageStrategy
from domain.models.ad_strategy.ad_strategy import AdStrategy
from domain.models.creative_strategy.creative_strategy import CreativeStrategy
from domain.models.ad_execution.ad_execution import AdExecution
from domain.models.creative_execution.creative_execution import CreativeExecution
from domain.models.ugc_creatives.ugc_creative import UgcCreative
from domain.models.page_strategy.page_strategy import PageStrategy
from domain.models.page_requirements.page_requirements import PageRequirements
from domain.models.page_blueprint.page_blueprint import PageBlueprint
from domain.models.page_content_plan.page_content_plan import PageContentPlan
from domain.models.page_copy.page_copy import PageCopy

# Table name -> model, for the entities that have their own list + detail
# page in the frontend (and can therefore be marked as favorite).
FAVORITABLE_MODELS: Dict[str, Type[Base]] = {
    TableName.OFFERS_RAW.value: OfferRaw,
    TableName.OFFER_PROFILE.value: OfferProfile,
    TableName.TARGET_AUDIENCES.value: TargetAudience,
    TableName.ANALYSIS.value: Analysis,
    TableName.CHECKLIST.value: Checklist,
    TableName.BRAND_MARKETING.value: BrandMarketing,
    TableName.MARKETING_STRATEGY.value: MarketingStrategy,
    TableName.OFFER_STRATEGY.value: OfferStrategy,
    TableName.MESSAGE_STRATEGY.value: MessageStrategy,
    TableName.AD_STRATEGY.value: AdStrategy,
    TableName.CREATIVE_STRATEGY.value: CreativeStrategy,
    TableName.AD_EXECUTION.value: AdExecution,
    TableName.CREATIVE_EXECUTIONS.value: CreativeExecution,
    TableName.UGC_CREATIVES.value: UgcCreative,
    TableName.PAGE_STRATEGY.value: PageStrategy,
    TableName.PAGE_REQUIREMENTS.value: PageRequirements,
    TableName.PAGE_BLUEPRINT.value: PageBlueprint,
    TableName.PAGE_CONTENT_PLAN.value: PageContentPlan,
    TableName.PAGE_COPY.value: PageCopy,
}

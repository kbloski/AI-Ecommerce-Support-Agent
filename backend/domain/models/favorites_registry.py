from typing import Dict, Type

from infrastructure.database.db import Base
from domain.enums.table_name import TableName
from domain.models.offer.offer_raw import OfferRaw
from domain.models.offer.offer_source import OfferSource
from domain.models.audience.target_audience import TargetAudience
from domain.models.analysis.analysis import Analysis
from domain.models.checklist.checklist import Checklist
from domain.models.creative.ugc_creative import UgcCreative
from domain.models.page.page_blueprint import PageBlueprint
from domain.models.page.page import Page

# Table name -> model, for the entities that have their own list + detail
# page in the frontend (and can therefore be marked as favorite).
FAVORITABLE_MODELS: Dict[str, Type[Base]] = {
    TableName.OFFERS_RAW.value: OfferRaw,
    TableName.OFFER_SOURCES.value: OfferSource,
    TableName.TARGET_AUDIENCES.value: TargetAudience,
    TableName.ANALYSIS.value: Analysis,
    TableName.CHECKLIST.value: Checklist,
    TableName.UGC_CREATIVES.value: UgcCreative,
    TableName.PAGE_BLUEPRINT.value: PageBlueprint,
    TableName.PAGES.value: Page,
}

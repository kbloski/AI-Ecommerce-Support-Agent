from typing import Any, Dict, Optional, Tuple, Union

from di.container import Container
from domain.enums.pipeline_entity_type import PipelineEntityType

from application.handlers.offers.get_offer import get_offer_handler
from application.handlers.offer_profiles.get_offer_profile_handler import get_offer_profile_handler
from application.handlers.brand_marketing.get_brand_marketing_handler import get_brand_marketing_handler
from application.handlers.marketing_strategy.get_marketing_strategy_handler import get_marketing_strategy_handler
from application.handlers.offer_strategy.get_offer_strategy_handler import get_offer_strategy_handler
from application.handlers.message_strategy.get_message_strategy_handler import get_message_strategy_handler
from application.handlers.ad_strategy.get_ad_strategy_handler import get_ad_strategy_handler
from application.handlers.creative_strategy.get_creative_strategy_handler import get_creative_strategy_handler
from application.handlers.ad_execution.get_ad_execution_handler import get_ad_execution_handler
from application.handlers.creative_execution.get_creative_execution_handler import get_creative_execution_handler
from application.handlers.ugc_creatives.get_ugc_creative_handler import get_ugc_creative_handler
from application.handlers.page_strategy.get_page_strategy_handler import get_page_strategy_handler
from application.handlers.page_requirements.get_page_requirements_handler import get_page_requirements_handler
from application.handlers.page_blueprint.get_page_blueprint_handler import get_page_blueprint_handler
from application.handlers.page_content_plan.get_page_content_plan_handler import get_page_content_plan_handler
from application.handlers.page_copy.get_page_copy_handler import get_page_copy_handler


# Dla każdego etapu: jak pobrać jego własne DTO (istniejący get_*_handler),
# który serwis w kontenerze DI udostępnia build_llm_context() dla tego etapu
# (None = liść — nic dalej w pipeline'ie nie generuje się z jego kontekstu),
# oraz przez które pole i do jakiego etapu prowadzi rodzic. W górę łańcuch
# nigdy się nie rozgałęzia, więc (entity_type, entity_id) zawsze wyznacza
# dokładnie jedną ścieżkę z powrotem do Offer.
STAGE_CONFIG: Dict[PipelineEntityType, Dict[str, Any]] = {
    PipelineEntityType.OFFER: {
        "get_handler": get_offer_handler,
        "context_service": "offer_service",
        "parent_field": None,
        "parent_stage": None,
    },
    PipelineEntityType.OFFER_PROFILE: {
        "get_handler": get_offer_profile_handler,
        "context_service": "offer_profile_service",
        "parent_field": "offer_id",
        "parent_stage": PipelineEntityType.OFFER,
    },
    PipelineEntityType.BRAND_MARKETING: {
        "get_handler": get_brand_marketing_handler,
        "context_service": "brand_marketing_service",
        "parent_field": "offer_profile_id",
        "parent_stage": PipelineEntityType.OFFER_PROFILE,
    },
    PipelineEntityType.MARKETING_STRATEGY: {
        "get_handler": get_marketing_strategy_handler,
        "context_service": "marketing_strategy_service",
        "parent_field": "brand_marketing_id",
        "parent_stage": PipelineEntityType.BRAND_MARKETING,
    },
    PipelineEntityType.OFFER_STRATEGY: {
        "get_handler": get_offer_strategy_handler,
        "context_service": "offer_strategy_service",
        "parent_field": "marketing_strategy_id",
        "parent_stage": PipelineEntityType.MARKETING_STRATEGY,
    },
    PipelineEntityType.MESSAGE_STRATEGY: {
        "get_handler": get_message_strategy_handler,
        "context_service": "message_strategy_service",
        "parent_field": "offer_strategy_id",
        "parent_stage": PipelineEntityType.OFFER_STRATEGY,
    },
    PipelineEntityType.AD_STRATEGY: {
        "get_handler": get_ad_strategy_handler,
        "context_service": "ad_strategy_service",
        "parent_field": "message_strategy_id",
        "parent_stage": PipelineEntityType.MESSAGE_STRATEGY,
    },
    PipelineEntityType.CREATIVE_STRATEGY: {
        "get_handler": get_creative_strategy_handler,
        "context_service": "creative_strategy_service",
        "parent_field": "ad_strategy_id",
        "parent_stage": PipelineEntityType.AD_STRATEGY,
    },
    PipelineEntityType.AD_EXECUTION: {
        "get_handler": get_ad_execution_handler,
        "context_service": "ad_execution_service",
        "parent_field": "creative_strategy_id",
        "parent_stage": PipelineEntityType.CREATIVE_STRATEGY,
    },
    PipelineEntityType.CREATIVE_EXECUTION: {
        "get_handler": get_creative_execution_handler,
        "context_service": None,  # liść gałęzi ADS
        "parent_field": "ad_execution_id",
        "parent_stage": PipelineEntityType.AD_EXECUTION,
    },
    PipelineEntityType.UGC_CREATIVE: {
        "get_handler": get_ugc_creative_handler,
        "context_service": None,  # liść gałęzi UGC
        "parent_field": "message_strategy_id",
        "parent_stage": PipelineEntityType.MESSAGE_STRATEGY,
    },
    PipelineEntityType.PAGE_STRATEGY: {
        "get_handler": get_page_strategy_handler,
        "context_service": "page_strategy_service",
        "parent_field": "message_strategy_id",
        "parent_stage": PipelineEntityType.MESSAGE_STRATEGY,
    },
    PipelineEntityType.PAGE_REQUIREMENTS: {
        "get_handler": get_page_requirements_handler,
        "context_service": "page_requirements_service",
        "parent_field": "page_strategy_id",
        "parent_stage": PipelineEntityType.PAGE_STRATEGY,
    },
    PipelineEntityType.PAGE_BLUEPRINT: {
        "get_handler": get_page_blueprint_handler,
        "context_service": "page_blueprint_service",
        # Nowsze rekordy mają page_requirements_id; starsze (sprzed
        # wprowadzenia etapu PageRequirements) tylko page_strategy_id —
        # zob. known-issues.md ("additive migration" w init_db.py).
        "parent_field": ("page_requirements_id", "page_strategy_id"),
        "parent_stage": (PipelineEntityType.PAGE_REQUIREMENTS, PipelineEntityType.PAGE_STRATEGY),
    },
    PipelineEntityType.PAGE_CONTENT_PLAN: {
        "get_handler": get_page_content_plan_handler,
        "context_service": "page_content_plan_service",
        "parent_field": "page_blueprint_id",
        "parent_stage": PipelineEntityType.PAGE_BLUEPRINT,
    },
    PipelineEntityType.PAGE_COPY: {
        "get_handler": get_page_copy_handler,
        "context_service": None,  # liść gałęzi PAGE
        "parent_field": "page_content_plan_id",
        "parent_stage": PipelineEntityType.PAGE_CONTENT_PLAN,
    },
}


def _resolve_parent(
    dto: Any,
    parent_field: Union[str, Tuple[str, ...], None],
    parent_stage: Union[PipelineEntityType, Tuple[PipelineEntityType, ...], None],
) -> Tuple[Optional[int], Optional[PipelineEntityType]]:
    if parent_field is None:
        return None, None

    if isinstance(parent_field, tuple):
        for field, stage in zip(parent_field, parent_stage):
            value = getattr(dto, field, None)
            if value is not None:
                return value, stage
        return None, None

    return getattr(dto, parent_field, None), parent_stage


def get_pipeline_path_handler(entity_type: PipelineEntityType, entity_id: int) -> Dict[str, Any]:
    if entity_type not in STAGE_CONFIG:
        raise ValueError(f"Nieznany typ elementu pipeline'u: {entity_type}")

    container = Container()

    path = []
    current_stage, current_id = entity_type, entity_id

    while current_stage is not None:
        config = STAGE_CONFIG[current_stage]
        dto = config["get_handler"](current_id)

        if dto is None:
            raise ValueError(f"Nie znaleziono {current_stage.value} o id={current_id}")

        llm_context = None
        context_service_name = config["context_service"]
        if context_service_name is not None:
            service = getattr(container, context_service_name)()
            llm_context = service.build_llm_context(current_id)

        path.append({
            "stage": current_stage.value,
            "id": current_id,
            "data": dto.to_dict(),
            "llm_context": llm_context,
        })

        current_id, current_stage = _resolve_parent(dto, config["parent_field"], config["parent_stage"])

    path.reverse()

    return {
        "requested": {"entity_type": entity_type.value, "entity_id": entity_id},
        "path": path,
    }

from fastapi import HTTPException

from application.services.llm_context_composer import ContextRef, ContextSelection
from domain.enums.context_type import ContextType


RESOURCE_TYPES = {ContextType.OFFER_RAW, ContextType.OFFER_SOURCE, ContextType.OFFER_PROFILE}


def compose_resource_context(
    container,
    resource_type: ContextType,
    resource_id: int,
    include: list[ContextType],
    marketing_angle_ids: list[int],
    include_offer_facts: bool = True,
    include_additional_contexts: bool = True,
    order_by_path: bool = False,
    ad_concept_ids: list[int] | None = None,
    creative_plan_ids: list[int] | None = None,
    ugc_creative_ids: list[int] | None = None,
    ad_copy_ids: list[int] | None = None,
    target_audience_ids: list[int] | None = None,
) -> str:
    ad_concept_ids = ad_concept_ids or []
    selected_ids = {
        ContextType.MARKETING_ANGLE: marketing_angle_ids,
        ContextType.AD_CONCEPT: ad_concept_ids,
        ContextType.CREATIVE_PLAN: creative_plan_ids or [],
        ContextType.UGC_CREATIVE: ugc_creative_ids or [],
        ContextType.AD_COPY: ad_copy_ids or [],
    }
    target_audience_ids = target_audience_ids or []
    if target_audience_ids:
        selected_ids[ContextType.TARGET_AUDIENCES] = target_audience_ids
    if resource_type not in RESOURCE_TYPES:
        raise HTTPException(422, f"Unsupported resource type: {resource_type.value}")
    if len(include) != len(set(include)):
        raise HTTPException(422, "Context selections must be unique")
    if resource_type == ContextType.OFFER_RAW and (include or any(selected_ids.values())):
        raise HTTPException(422, "Raw offer does not support related context")
    if resource_type != ContextType.OFFER_PROFILE and not include_additional_contexts:
        raise HTTPException(422, "Additional contexts can only be selected for an offer profile")
    if resource_type == ContextType.OFFER_SOURCE and (set(include) - {ContextType.OFFER_RAW} or any(selected_ids.values())):
        raise HTTPException(422, "Offer source can only include its raw offer")
    for kind, ids in selected_ids.items():
        if ids and kind not in include:
            raise HTTPException(422, f"Select {kind.value} in include")
        if kind in include and not ids:
            raise HTTPException(422, f"Select at least one {kind.value}")
        if len(ids) != len(set(ids)):
            raise HTTPException(422, f"Select unique {kind.value} IDs")

    selections = []
    for type in include:
        if type in selected_ids:
            selections.append(ContextSelection(type, include_ids=tuple(selected_ids[type])))
        elif type in (ContextType.OFFER_RAW, ContextType.OFFER_SOURCE, ContextType.TARGET_AUDIENCES):
            selections.append(ContextSelection(type))
        else:
            raise HTTPException(422, f"Unsupported profile context selection: {type.value}")

    if resource_type == ContextType.OFFER_SOURCE:
        if container.offer_source_repository().get_by_id(resource_id) is None:
            raise HTTPException(404, "Offer source not found")
    try:
        options = {"root": ContextRef(resource_type, resource_id), "include": selections}
        if order_by_path:
            options["order_by_path"] = True
        if not include_offer_facts:
            options["include_offer_facts"] = False
        if not include_additional_contexts:
            options["include_additional_contexts"] = False
        return container.llm_context_composer().compose(**options)
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    except ValueError as error:
        raise HTTPException(422, str(error)) from error

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
) -> str:
    ad_concept_ids = ad_concept_ids or []
    if resource_type not in RESOURCE_TYPES:
        raise HTTPException(422, f"Unsupported resource type: {resource_type.value}")
    if len(include) != len(set(include)):
        raise HTTPException(422, "Context selections must be unique")
    if resource_type == ContextType.OFFER_RAW and (include or marketing_angle_ids or ad_concept_ids):
        raise HTTPException(422, "Raw offer does not support related context")
    if resource_type != ContextType.OFFER_PROFILE and not include_additional_contexts:
        raise HTTPException(422, "Additional contexts can only be selected for an offer profile")
    if resource_type == ContextType.OFFER_SOURCE and (set(include) - {ContextType.OFFER_RAW} or marketing_angle_ids or ad_concept_ids):
        raise HTTPException(422, "Offer source can only include its raw offer")
    if marketing_angle_ids and ContextType.MARKETING_ANGLE not in include:
        raise HTTPException(422, "Select marketing angles in include")
    if ContextType.MARKETING_ANGLE in include and not marketing_angle_ids:
        raise HTTPException(422, "Select at least one marketing angle")
    if ad_concept_ids and ContextType.AD_CONCEPT not in include:
        raise HTTPException(422, "Select ad concepts in include")
    if ContextType.AD_CONCEPT in include and not ad_concept_ids:
        raise HTTPException(422, "Select at least one ad concept")

    selections = []
    for type in include:
        if type == ContextType.MARKETING_ANGLE:
            selections.append(ContextSelection(type, include_ids=tuple(marketing_angle_ids)))
        elif type == ContextType.AD_CONCEPT:
            selections.append(ContextSelection(type, include_ids=tuple(ad_concept_ids)))
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

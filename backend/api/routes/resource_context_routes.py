from fastapi import APIRouter, Path, Query
from fastapi.responses import Response

from application.services.resource_context_service import compose_resource_context
from di.container import Container
from domain.enums.context_type import ContextType


router = APIRouter()


@router.get("/resources/{resource_type}/{resource_id}/context")
def preview_resource_context(
    resource_type: ContextType,
    resource_id: int = Path(gt=0),
    include: list[ContextType] = Query(default=[]),
    marketing_angle_ids: list[int] = Query(default=[]),
    ad_concept_ids: list[int] = Query(default=[]),
    include_offer_facts: bool = Query(default=True),
    include_additional_contexts: bool = Query(default=True),
):
    content = compose_resource_context(
        Container(), resource_type, resource_id, include, marketing_angle_ids,
        include_offer_facts, include_additional_contexts, order_by_path=True,
        ad_concept_ids=ad_concept_ids,
    )
    return Response(content=content, media_type="text/plain; charset=utf-8")


@router.get("/resources/{resource_type}/{resource_id}/context/download")
def download_resource_context(
    resource_type: ContextType,
    resource_id: int = Path(gt=0),
    include: list[ContextType] = Query(default=[]),
    marketing_angle_ids: list[int] = Query(default=[]),
    ad_concept_ids: list[int] = Query(default=[]),
    include_offer_facts: bool = Query(default=True),
    include_additional_contexts: bool = Query(default=True),
):
    content = compose_resource_context(
        Container(), resource_type, resource_id, include, marketing_angle_ids,
        include_offer_facts, include_additional_contexts, order_by_path=True,
        ad_concept_ids=ad_concept_ids,
    )
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{resource_type.value}_{resource_id}_context.txt"'},
    )

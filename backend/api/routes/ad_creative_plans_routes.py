from fastapi import APIRouter

from application.dtos.ad_creative_plans.creative_plan_fields import (
    CreateCreativePlanRequest, GenerateCreativePlansRequest, UpdateCreativePlanRequest,
)
from application.handlers.ad_creative_plans.creative_plan_handlers import (
    create_creative_plan_handler, delete_creative_plan_handler,
    list_creative_plans_handler, update_creative_plan_handler,
)
from application.handlers.ad_creative_plans.generate_ad_creative_plans_handler import generate_ad_creative_plans_handler

router = APIRouter()


@router.get("/offer-profiles/{offer_profile_id}/creative-plans")
def list_creative_plans(offer_profile_id: int):
    return list_creative_plans_handler(offer_profile_id)


@router.post("/offer-profiles/{offer_profile_id}/creative-plans/generate")
def generate_creative_plans(offer_profile_id: int, payload: GenerateCreativePlansRequest):
    return generate_ad_creative_plans_handler(offer_profile_id, payload)


@router.post("/offer-profiles/{offer_profile_id}/creative-plans", status_code=201)
def create_creative_plan(offer_profile_id: int, payload: CreateCreativePlanRequest):
    return create_creative_plan_handler(offer_profile_id, payload)


@router.post("/creative-plans/{id}/update")
def update_creative_plan(id: int, payload: UpdateCreativePlanRequest):
    return update_creative_plan_handler(id, payload)


@router.delete("/creative-plans/{id}/delete")
def delete_creative_plan(id: int):
    return delete_creative_plan_handler(id)

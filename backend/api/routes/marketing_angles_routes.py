from fastapi import APIRouter

from application.dtos.marketing_angles.marketing_angle_fields import (
    GenerateMarketingAnglesRequest,
    MarketingAngleFields,
    UpdateMarketingAngleRequest,
)
from application.handlers.marketing_angles.list_marketing_angles_handler import list_marketing_angles_handler
from application.handlers.marketing_angles.generate_marketing_angles_handler import generate_marketing_angles_handler
from application.handlers.marketing_angles.create_marketing_angle_handler import create_marketing_angle_handler
from application.handlers.marketing_angles.update_marketing_angle_handler import update_marketing_angle_handler
from application.handlers.marketing_angles.delete_marketing_angle_handler import delete_marketing_angle_handler


router = APIRouter()


@router.get("/offer-profiles/{offer_profile_id}/marketing-angles")
def list_marketing_angles(offer_profile_id: int):
    return list_marketing_angles_handler(offer_profile_id)


@router.post("/offer-profiles/{offer_profile_id}/marketing-angles/generate")
def generate_marketing_angles(offer_profile_id: int, payload: GenerateMarketingAnglesRequest):
    return generate_marketing_angles_handler(offer_profile_id, payload)


@router.post("/offer-profiles/{offer_profile_id}/marketing-angles", status_code=201)
def create_marketing_angle(offer_profile_id: int, payload: MarketingAngleFields):
    return create_marketing_angle_handler(offer_profile_id, payload)


@router.post("/marketing-angles/{id}/update")
def update_marketing_angle(id: int, payload: UpdateMarketingAngleRequest):
    return update_marketing_angle_handler(id, payload)


@router.delete("/marketing-angles/{id}/delete")
def delete_marketing_angle(id: int):
    return delete_marketing_angle_handler(id)

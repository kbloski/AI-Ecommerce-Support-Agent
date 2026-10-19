from fastapi import APIRouter, Path

from application.dtos.brand_styles.brand_style_fields import BrandStyleFields, GenerateBrandStyleRequest
from application.handlers.brand_styles.brand_style_handlers import (
    create_brand_style_handler, delete_brand_style_handler,
    list_brand_styles_handler, update_brand_style_handler,
)
from application.handlers.brand_styles.generate_brand_style_handler import generate_brand_style_handler

router = APIRouter()


@router.get("/offer-profiles/{offer_profile_id}/brand-styles")
def list_brand_styles(offer_profile_id: int = Path(gt=0)):
    return list_brand_styles_handler(offer_profile_id)


@router.post("/offer-profiles/{offer_profile_id}/brand-styles/generate", status_code=201)
def generate_brand_style(payload: GenerateBrandStyleRequest, offer_profile_id: int = Path(gt=0)):
    return generate_brand_style_handler(offer_profile_id, payload)


@router.post("/offer-profiles/{offer_profile_id}/brand-styles", status_code=201)
def create_brand_style(payload: BrandStyleFields, offer_profile_id: int = Path(gt=0)):
    return create_brand_style_handler(offer_profile_id, payload)


@router.post("/brand-styles/{id}/update")
def update_brand_style(payload: BrandStyleFields, id: int = Path(gt=0)):
    return update_brand_style_handler(id, payload)


@router.delete("/brand-styles/{id}/delete")
def delete_brand_style(id: int = Path(gt=0)):
    return delete_brand_style_handler(id)

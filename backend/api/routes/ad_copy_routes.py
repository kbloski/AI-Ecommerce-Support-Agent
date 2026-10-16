from fastapi import APIRouter
from di.container import Container

from application.dtos.ad_copy.ad_copy_fields import AdCopyFields, GenerateAdCopyRequest, UpdateAdCopyRequest
from application.handlers.ad_copy.ad_copy_handlers import (
    list_ad_copies_handler, create_ad_copy_handler, update_ad_copy_handler, delete_ad_copy_handler,
)
from application.handlers.ad_copy.generate_ad_copy_handler import generate_ad_copy_handler

router = APIRouter()


@router.get("/ad-copy-structures")
def list_ad_copy_structures():
    return Container().ad_copy_structures_repository().get_all()


@router.get("/offer-profiles/{offer_profile_id}/ad-copies")
def list_ad_copies(offer_profile_id: int):
    return list_ad_copies_handler(offer_profile_id)


@router.post("/offer-profiles/{offer_profile_id}/ad-copies/generate")
def generate_ad_copies(offer_profile_id: int, payload: GenerateAdCopyRequest):
    return generate_ad_copy_handler(offer_profile_id, payload)


@router.post("/offer-profiles/{offer_profile_id}/ad-copies", status_code=201)
def create_ad_copy(offer_profile_id: int, payload: AdCopyFields):
    return create_ad_copy_handler(offer_profile_id, payload)


@router.post("/ad-copies/{id}/update")
def update_ad_copy(id: int, payload: UpdateAdCopyRequest):
    return update_ad_copy_handler(id, payload)


@router.delete("/ad-copies/{id}/delete")
def delete_ad_copy(id: int):
    return delete_ad_copy_handler(id)

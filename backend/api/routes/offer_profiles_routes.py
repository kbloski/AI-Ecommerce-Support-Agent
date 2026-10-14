from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field
from application.handlers.offer_profiles.create_offer_profile_handler import create_offer_profile_handler
from application.handlers.offer_profiles.list_offer_profiles_handler import list_offer_profiles_handler

from application.handlers.offer_profiles.get_offer_profile_handler import get_offer_profile_handler
from application.handlers.offer_profiles.update_offer_profile_handler import update_offer_profile_handler
from application.handlers.offer_profiles.delete_offer_profile_handler import delete_offer_profile_handler

router = APIRouter()

class CreateOfferProfileRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=255)

@router.get("/offer-sources/{offer_source_id}/profiles")
def list_profiles(offer_source_id: int):
    return list_offer_profiles_handler(offer_source_id)

@router.post("/offer-sources/{offer_source_id}/profiles", status_code=201)
def create_profile(offer_source_id: int, payload: CreateOfferProfileRequest):
    return create_offer_profile_handler(offer_source_id, payload.name)



@router.get("/offer-profiles/{id}")
def get_profile(id: int):
    return get_offer_profile_handler(id)

@router.post("/offer-profiles/{id}/update")
def update_profile(id: int, payload: CreateOfferProfileRequest):
    return update_offer_profile_handler(id, payload.name)

@router.delete("/offer-profiles/{id}/delete")
def delete_profile(id: int):
    return delete_offer_profile_handler(id)

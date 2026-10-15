from fastapi import APIRouter

from application.dtos.ad_concepts.ad_concept_fields import CreateAdConceptRequest, GenerateAdConceptsRequest, UpdateAdConceptRequest
from application.handlers.ad_concepts.list_ad_concepts_handler import list_ad_concepts_handler
from application.handlers.ad_concepts.generate_ad_concepts_handler import generate_ad_concepts_handler
from application.handlers.ad_concepts.create_ad_concept_handler import create_ad_concept_handler
from application.handlers.ad_concepts.update_ad_concept_handler import update_ad_concept_handler
from application.handlers.ad_concepts.delete_ad_concept_handler import delete_ad_concept_handler


router = APIRouter()


@router.get("/offer-profiles/{offer_profile_id}/ad-concepts")
def list_ad_concepts(offer_profile_id: int):
    return list_ad_concepts_handler(offer_profile_id)


@router.post("/offer-profiles/{offer_profile_id}/ad-concepts/generate")
def generate_ad_concepts(offer_profile_id: int, payload: GenerateAdConceptsRequest):
    return generate_ad_concepts_handler(offer_profile_id, payload)


@router.post("/offer-profiles/{offer_profile_id}/ad-concepts", status_code=201)
def create_ad_concept(offer_profile_id: int, payload: CreateAdConceptRequest):
    return create_ad_concept_handler(offer_profile_id, payload)


@router.post("/ad-concepts/{id}/update")
def update_ad_concept(id: int, payload: UpdateAdConceptRequest):
    return update_ad_concept_handler(id, payload)


@router.delete("/ad-concepts/{id}/delete")
def delete_ad_concept(id: int):
    return delete_ad_concept_handler(id)

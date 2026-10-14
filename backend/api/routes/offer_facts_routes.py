from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError
from application.dtos.offer_facts.offer_fact_fields import FactFields
from application.handlers.offer_facts.list_offer_facts_handler import list_offer_facts_handler
from application.handlers.offer_facts.create_offer_fact_handler import create_offer_fact_handler
from application.handlers.offer_facts.update_offer_fact_handler import update_offer_fact_handler
from application.handlers.offer_facts.delete_offer_fact_handler import delete_offer_fact_handler
from application.handlers.offer_facts.generate_offer_facts_handler import generate_offer_facts_handler
from pydantic import BaseModel
from typing import Any

router = APIRouter()

class UpdateFactRequest(BaseModel):
    fields: dict[str, Any]

@router.get("/offer-sources/{offer_source_id}/facts")
def list_facts(offer_source_id: int, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), search: str | None = None, is_reviewed: bool | None = None, sort: Literal["created_at_desc", "created_at_asc", "name_asc", "name_desc"] = "created_at_desc"):
    return list_offer_facts_handler(offer_source_id, page=page, page_size=page_size, search=search, is_reviewed=is_reviewed, sort=sort)

@router.post("/offer-sources/{offer_source_id}/facts/generate")
def generate_facts(offer_source_id: int):
    return generate_offer_facts_handler(offer_source_id)

@router.post("/offer-sources/{offer_source_id}/facts", status_code=201)
def create_fact(offer_source_id: int, payload: FactFields):
    try:
        return create_offer_fact_handler(offer_source_id, payload)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error

@router.post("/offer-facts/{id}/update")
def update_fact(id: int, payload: UpdateFactRequest):
    try:
        return update_offer_fact_handler(id, payload.fields)
    except (ValueError, ValidationError) as error:
        raise HTTPException(422, str(error)) from error

@router.delete("/offer-facts/{id}/delete")
def delete_fact(id: int):
    return delete_offer_fact_handler(id)

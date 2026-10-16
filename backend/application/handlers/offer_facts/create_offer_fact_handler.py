from fastapi import HTTPException
from di.container import Container
from application.mappers.offer_fact_mapper import offer_fact_to_dict as to_dict
from domain.models.offer.offer_fact import OfferFact


def create_offer_fact_handler(offer_source_id, fields):
    container = Container()
    material = source_material(container, offer_source_id)
    validate_evidence(fields, material)
    fact = OfferFact(offer_source_id=offer_source_id, **fields.model_dump())
    return to_dict(container.offer_facts_repository().create_many([fact])[0])


def normalize(value):
    return " ".join((value or "").split()).casefold()


def source_material(container, offer_source_id):
    source = container.offer_source_repository().get_by_id(offer_source_id)
    if source is None:
        raise HTTPException(404, "Offer source not found")
    return {"offer_details": source.offer_details or ""}


def validate_evidence(fields, material):
    if fields.evidence and not any(normalize(fields.evidence) in normalize(value) for value in material.values()):
        raise ValueError("Evidence must quote the offer source")

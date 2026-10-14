from di.container import Container
from application.mappers.offer_fact_mapper import offer_fact_to_dict as to_dict
from fastapi import HTTPException
from application.dtos.offer_facts.offer_fact_fields import FactFields


def update_offer_fact_handler(id, updates):
    container = Container()
    repo = container.offer_facts_repository()
    fact = repo.get_by_id(id)
    if fact is None:
        raise HTTPException(404, "Offer fact not found")
    current = {key: getattr(fact, key) for key in FactFields.model_fields}
    if set(updates) - set(current):
        raise ValueError("Unsupported fact fields")
    # Changing factual content invalidates an earlier review.
    changed = any(key != "is_reviewed" and value != current[key] for key, value in updates.items())
    fields = FactFields.model_validate({**current, **updates, **({"is_reviewed": False} if changed else {})})
    validate_evidence(fields, source_material(container, fact.offer_source_id))
    for key, value in fields.model_dump().items():
        setattr(fact, key, value)
    return to_dict(repo.update(fact))


def normalize(value):
    return " ".join((value or "").split()).casefold()


def source_material(container, offer_source_id):
    source = container.offer_source_repository().get_by_id(offer_source_id)
    if source is None:
        raise HTTPException(404, "Offer source not found")
    return {"offer_summary": source.offer_summary or ""}


def validate_evidence(fields, material):
    if fields.evidence and not any(normalize(fields.evidence) in normalize(value) for value in material.values()):
        raise ValueError("Evidence must quote the offer source")

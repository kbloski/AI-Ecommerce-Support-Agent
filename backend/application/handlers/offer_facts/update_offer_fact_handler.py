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
    for key, value in fields.model_dump().items():
        setattr(fact, key, value)
    return to_dict(repo.update(fact))

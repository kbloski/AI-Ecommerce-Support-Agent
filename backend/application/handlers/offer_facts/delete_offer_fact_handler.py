from fastapi import HTTPException
from di.container import Container


def delete_offer_fact_handler(id):
    repo = Container().offer_facts_repository()
    fact = repo.get_by_id(id)
    if fact is None:
        raise HTTPException(404, "Offer fact not found")
    repo.delete(fact)
    return {"deleted": True}

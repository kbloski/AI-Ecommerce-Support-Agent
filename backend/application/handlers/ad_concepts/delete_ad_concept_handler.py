from fastapi import HTTPException

from di.container import Container


def delete_ad_concept_handler(id: int):
    repo = Container().ad_concepts_repository()
    item = repo.get_by_id(id)
    if item is None:
        raise HTTPException(404, "Ad concept not found")
    repo.delete(item)
    return {"deleted": True}

from fastapi import HTTPException

from application.mappers.ad_copy_mapper import ad_copy_to_dict
from domain.models.ad.ad_copy import AdCopy
from di.container import Container


def require_profile(container, offer_profile_id):
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")


def list_ad_copies_handler(offer_profile_id):
    container = Container()
    require_profile(container, offer_profile_id)
    return [ad_copy_to_dict(item) for item in container.ad_copies_repository().find_for_offer_profile(offer_profile_id)]


def create_ad_copy_handler(offer_profile_id, request):
    container = Container()
    require_profile(container, offer_profile_id)
    item = AdCopy(offer_profile_id=offer_profile_id, **request.model_dump())
    return ad_copy_to_dict(container.ad_copies_repository().create_many([item])[0])


def update_ad_copy_handler(id, request):
    repo = Container().ad_copies_repository()
    item = repo.get_by_id(id)
    if item is None:
        raise HTTPException(404, "Ad copy not found")
    for key, value in request.model_dump().items():
        setattr(item, key, value)
    return ad_copy_to_dict(repo.update(item))


def delete_ad_copy_handler(id):
    repo = Container().ad_copies_repository()
    item = repo.get_by_id(id)
    if item is None:
        raise HTTPException(404, "Ad copy not found")
    repo.delete(item)
    return {"deleted": True}

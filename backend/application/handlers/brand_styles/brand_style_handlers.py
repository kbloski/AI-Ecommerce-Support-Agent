from fastapi import HTTPException

from application.mappers.brand_style_mapper import brand_style_to_dict
from domain.models.brand.brand_style import BrandStyle
from di.container import Container


def require_profile(container, offer_profile_id):
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")


def require_brand_style(repo, id):
    item = repo.get_by_id(id)
    if item is None:
        raise HTTPException(404, "Brand style not found")
    return item


def list_brand_styles_handler(offer_profile_id):
    container = Container()
    require_profile(container, offer_profile_id)
    return [brand_style_to_dict(item) for item in container.brand_styles_repository().find_for_offer_profile(offer_profile_id)]


def create_brand_style_handler(offer_profile_id, request):
    container = Container()
    require_profile(container, offer_profile_id)
    item = BrandStyle(offer_profile_id=offer_profile_id, **request.model_dump())
    return brand_style_to_dict(container.brand_styles_repository().create(item))


def update_brand_style_handler(id, request):
    repo = Container().brand_styles_repository()
    item = require_brand_style(repo, id)
    for key, value in request.model_dump().items():
        setattr(item, key, value)
    return brand_style_to_dict(repo.update(item))


def delete_brand_style_handler(id):
    repo = Container().brand_styles_repository()
    repo.delete(require_brand_style(repo, id))
    return {"deleted": True}

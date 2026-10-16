from fastapi import HTTPException

from application.mappers.ad_creative_plan_mapper import creative_plan_to_dict
from domain.models.ad.ad_creative_plan import AdCreativePlan
from di.container import Container


def require_profile(container, offer_profile_id):
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")


def selected_concept(container, offer_profile_id, ad_concept_id):
    if ad_concept_id is None:
        return None
    concept = container.ad_concepts_repository().get_by_id(ad_concept_id)
    if concept is None:
        raise HTTPException(404, "Ad concept not found")
    if concept.offer_profile_id != offer_profile_id:
        raise HTTPException(422, "Ad concept must belong to this offer profile")
    return concept


def list_creative_plans_handler(offer_profile_id):
    container = Container()
    require_profile(container, offer_profile_id)
    return [creative_plan_to_dict(item) for item in container.ad_creative_plans_repository().find_for_offer_profile(offer_profile_id)]


def create_creative_plan_handler(offer_profile_id, request):
    container = Container()
    require_profile(container, offer_profile_id)
    selected_concept(container, offer_profile_id, request.ad_concept_id)
    item = AdCreativePlan(offer_profile_id=offer_profile_id, **request.model_dump(mode="json"))
    return creative_plan_to_dict(container.ad_creative_plans_repository().create_many([item])[0])


def update_creative_plan_handler(id, request):
    container = Container()
    repo = container.ad_creative_plans_repository()
    item = repo.get_by_id(id)
    if item is None:
        raise HTTPException(404, "Creative plan not found")
    selected_concept(container, item.offer_profile_id, request.ad_concept_id)
    values = request.model_dump(mode="json", exclude={"is_reviewed"})
    changed = any(getattr(item, key) != value for key, value in values.items())
    for key, value in values.items():
        setattr(item, key, value)
    item.is_reviewed = False if changed else request.is_reviewed
    return creative_plan_to_dict(repo.update(item))


def delete_creative_plan_handler(id):
    repo = Container().ad_creative_plans_repository()
    item = repo.get_by_id(id)
    if item is None:
        raise HTTPException(404, "Creative plan not found")
    repo.delete(item)
    return {"deleted": True}

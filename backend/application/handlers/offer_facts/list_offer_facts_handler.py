from fastapi import HTTPException
from di.container import Container
from application.mappers.offer_fact_mapper import offer_fact_to_dict as to_dict


def list_offer_facts_handler(offer_source_id, **filters):
    container = Container()
    source_material(container, offer_source_id)
    result = container.offer_facts_repository().search_for_offer_source(offer_source_id, **filters)
    return result.to_dict(to_dict)


def source_material(container, offer_source_id):
    source = container.offer_source_repository().get_by_id(offer_source_id)
    if source is None:
        raise HTTPException(404, "Offer source not found")
    return {"offer_summary": source.offer_summary or ""}

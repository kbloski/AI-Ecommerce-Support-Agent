def offer_fact_to_dict(fact):
    return {key: getattr(fact, key) for key in (
        "id", "offer_source_id", "name", "description", "evidence", "is_reviewed", "created_at", "updated_at"
    )}

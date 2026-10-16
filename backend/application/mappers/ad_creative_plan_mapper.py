def creative_plan_to_dict(item):
    return {
        key: getattr(item, key)
        for key in (
            "id", "offer_profile_id", "ad_concept_id", "name", "description",
            "format", "plan", "is_reviewed", "created_at", "updated_at",
        )
    }

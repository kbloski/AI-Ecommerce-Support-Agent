def ad_copy_to_dict(item):
    return {key: getattr(item, key) for key in (
        "id", "offer_profile_id", "name", "primary_text", "headline", "description", "cta", "is_reviewed",
    )}

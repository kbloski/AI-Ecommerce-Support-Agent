def offer_profile_to_dict(profile):
    return {key: getattr(profile, key) for key in ("id", "offer_source_id", "name", "created_at")}

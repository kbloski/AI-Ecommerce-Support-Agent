def brand_style_to_dict(item):
    return {
        key: getattr(item, key)
        for key in (
            "id", "offer_profile_id", "font_family", "background_color",
            "brand_color", "created_at", "updated_at",
        )
    }

def additional_context_to_dict(context):
    return {key: getattr(context, key) for key in ("id", "name", "content", "created_at", "updated_at")}

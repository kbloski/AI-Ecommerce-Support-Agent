def note_to_dict(note):
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "is_pinned": note.is_pinned,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }

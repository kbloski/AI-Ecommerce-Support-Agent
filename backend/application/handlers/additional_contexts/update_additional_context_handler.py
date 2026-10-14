from fastapi import HTTPException
from di.container import Container
from application.mappers.additional_context_mapper import additional_context_to_dict


def update_additional_context_handler(id: int, name: str, content: str):
    repo = Container().additional_contexts_repository()
    context = repo.get_by_id(id)
    if context is None:
        raise HTTPException(404, "Additional context not found")
    context.name = name
    context.content = content
    return additional_context_to_dict(repo.update(context))

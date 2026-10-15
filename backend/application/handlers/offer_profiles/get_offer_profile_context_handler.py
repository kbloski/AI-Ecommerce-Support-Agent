import json
import re

from application.services.resource_context_service import compose_resource_context
from di.container import Container
from domain.enums.context_type import ContextType


_SECTION = re.compile(r'<(?P<tag>[a-z_]+)(?: purpose="[^"]*")?>\n(?P<body>.*?)\n</(?P=tag)>', re.DOTALL)


def _context_as_json(context: str) -> dict:
    sections = {}
    position = 0
    for match in _SECTION.finditer(context):
        if context[position:match.start()].strip():
            raise ValueError("Unexpected LLM context content")
        tag = match.group("tag")
        if tag in sections:
            raise ValueError(f"Duplicate LLM context section: {tag}")
        sections[tag] = json.loads(match.group("body"))
        position = match.end()
    if context[position:].strip():
        raise ValueError("Unexpected LLM context content")
    return sections


def get_offer_profile_context_handler(
    id: int,
    include: list[ContextType],
    marketing_angle_ids: list[int],
    ad_concept_ids: list[int],
):
    context = compose_resource_context(
        Container(), ContextType.OFFER_PROFILE, id, include, marketing_angle_ids,
        ad_concept_ids=ad_concept_ids,
    )
    return {"context": context, "sections": _context_as_json(context)}

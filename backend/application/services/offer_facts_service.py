import json

from application.mappers.offer_fact_mapper import offer_fact_to_dict
from application.services.llm_context_builder import build_llm_section
from infrastructure.repositories.offer_facts_repository import OfferFactsRepository


class OfferFactsService:
    def __init__(self, offer_facts_repository: OfferFactsRepository):
        self.offer_facts_repository = offer_facts_repository

    def build_llm_context(self, offer_source_id: int, *, include_unreviewed: bool = False) -> str:
        facts = self.offer_facts_repository.find_for_offer_source(offer_source_id)
        content = []
        for fact in facts:
            if not include_unreviewed and not fact.is_reviewed:
                continue
            data = offer_fact_to_dict(fact)
            content.append({key: data[key] for key in ("name", "description", "evidence")})
        purpose = (
            "Previously extracted facts for duplicate detection only; unreviewed facts are not evidence."
            if include_unreviewed else
            "Reviewed facts describing the offer."
        )
        return build_llm_section(
            "offer_facts", json.dumps(content, ensure_ascii=False, indent=2), purpose=purpose
        )

import json

from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose
from infrastructure.repositories.ad_concepts_repository import AdConceptsRepository


class AdConceptService:
    def __init__(self, ad_concepts_repository: AdConceptsRepository):
        self.ad_concepts_repository = ad_concepts_repository

    def build_llm_context(self, offer_profile_id: int, concept_ids: list[int]) -> str:
        if not concept_ids or len(concept_ids) != len(set(concept_ids)):
            raise ValueError("Select unique ad concepts")
        concepts = []
        for concept_id in concept_ids:
            concept = self.ad_concepts_repository.get_by_id(concept_id)
            if concept is None:
                raise LookupError(f"Ad concept {concept_id} not found")
            if concept.offer_profile_id != offer_profile_id:
                raise ValueError("Selected ad concepts must belong to this offer profile")
            concepts.append(concept)
        content = json.dumps([
            {
                "id": concept.id,
                "name": concept.name,
                "description": concept.description,
                "format": concept.format,
                "core_idea": concept.core_idea,
                "key_message": concept.key_message,
                "generation_mode": concept.generation_mode,
                "marketing_angle_ids": sorted(angle.id for angle in concept.marketing_angles),
            }
            for concept in concepts
        ], ensure_ascii=False, indent=2)
        return build_llm_section("ad_concepts", content, purpose=ContextSectionPurpose.AD_CONCEPT.value)

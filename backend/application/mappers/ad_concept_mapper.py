from domain.models.ad.ad_concept import AdConcept


def ad_concept_to_dict(concept: AdConcept) -> dict:
    return {
        "id": concept.id,
        "offer_profile_id": concept.offer_profile_id,
        "marketing_angle_ids": sorted(angle.id for angle in concept.marketing_angles),
        "generation_mode": concept.generation_mode,
        "name": concept.name,
        "description": concept.description,
        "format": concept.format,
        "core_idea": concept.core_idea,
        "key_message": concept.key_message,
        "is_reviewed": concept.is_reviewed,
        "created_at": concept.created_at,
        "updated_at": concept.updated_at,
    }

from domain.models.offer.marketing_angle import MarketingAngle


def marketing_angle_to_dict(angle: MarketingAngle) -> dict:
    return {
        "id": angle.id,
        "offer_profile_id": angle.offer_profile_id,
        "name": angle.name,
        "description": angle.description,
        "core_message": angle.core_message,
        "value_proposition": angle.value_proposition,
        "pain_point": angle.pain_point,
        "desire": angle.desire,
        "emotional_driver": angle.emotional_driver,
        "supporting_arguments": angle.supporting_arguments or [],
        "proof_points": angle.proof_points or [],
        "is_reviewed": angle.is_reviewed,
        "created_at": angle.created_at,
        "updated_at": angle.updated_at,
    }

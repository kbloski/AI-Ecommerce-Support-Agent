import json

from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose
from infrastructure.repositories.marketing_angles_repository import MarketingAnglesRepository


class MarketingAngleService:
    def __init__(self, marketing_angles_repository: MarketingAnglesRepository):
        self.marketing_angles_repository = marketing_angles_repository

    def get_selected_angles(self, offer_profile_id: int, angle_ids: list[int]):
        if len(angle_ids) != len(set(angle_ids)):
            raise ValueError("Marketing angles must be unique")
        angles = []
        for angle_id in angle_ids:
            angle = self.marketing_angles_repository.get_by_id(angle_id)
            if angle is None:
                raise LookupError(f"Marketing angle {angle_id} not found")
            if angle.offer_profile_id != offer_profile_id:
                raise ValueError("Selected marketing angles must belong to this offer profile")
            angles.append(angle)
        return angles

    def build_llm_context(self, offer_profile_id: int, angle_ids: list[int]) -> str:
        angles = self.get_selected_angles(offer_profile_id, angle_ids)
        content = json.dumps([{
            "id": angle.id,
            "name": angle.name,
            "description": angle.description,
            "core_message": angle.core_message,
            "value_proposition": angle.value_proposition,
            "pain_point": angle.pain_point,
            "desire": angle.desire,
            "emotional_driver": angle.emotional_driver,
            "supporting_arguments": angle.supporting_arguments or [],
            "proof_points": angle.proof_points or [],
        } for angle in angles], ensure_ascii=False, indent=2)
        return build_llm_section(
            "marketing_angles", content, purpose=ContextSectionPurpose.MARKETING_ANGLE.value,
        )

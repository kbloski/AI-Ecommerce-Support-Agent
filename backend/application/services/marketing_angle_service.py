import json

from application.services.llm_context_builder import build_llm_section
from domain.enums.context_section_purpose import ContextSectionPurpose
from infrastructure.repositories.marketing_angles_repository import MarketingAnglesRepository


class MarketingAngleService:
    def __init__(self, marketing_angles_repository: MarketingAnglesRepository):
        self.marketing_angles_repository = marketing_angles_repository

    def build_llm_context(self, offer_profile_id: int, marketing_angle_id: int) -> str:
        angle = self.marketing_angles_repository.get_by_id(marketing_angle_id)
        if angle is None:
            raise LookupError(f"Marketing angle {marketing_angle_id} not found")
        if angle.offer_profile_id != offer_profile_id:
            raise ValueError("Selected marketing angle must belong to this offer profile")
        content = json.dumps({
            "name": angle.name,
            "description": angle.description,
            "core_message": angle.core_message,
            "value_proposition": angle.value_proposition,
            "pain_point": angle.pain_point,
            "desire": angle.desire,
            "emotional_driver": angle.emotional_driver,
            "supporting_arguments": angle.supporting_arguments or [],
            "proof_points": angle.proof_points or [],
        }, ensure_ascii=False, indent=2)
        return build_llm_section(
            "marketing_angle", content, purpose=ContextSectionPurpose.MARKETING_ANGLE.value,
        )

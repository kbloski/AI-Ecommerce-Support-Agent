from domain.models.audience.target_audience import TargetAudience
from application.dtos.audience.target_audience_dto import TargetAudienceDto


class TargetAudienceMapper:

    @staticmethod
    def to_dto(item: TargetAudience) -> TargetAudienceDto:
        return TargetAudienceDto(
            id=item.id,
            offer_profile_id=item.offer_profile_id,
            fact_status=item.fact_status,
            review_status=item.review_status,

            name=item.name,
            reason=item.reason,

            score=item.score,
            confidence=item.confidence,

            age_min=item.age_min,
            age_max=item.age_max,
            gender=item.gender,
            location=item.location,
            purchasing_power=item.purchasing_power,

            lifestyles=item.lifestyles,
            values=item.values,

            awareness_level=item.awareness_level,
            price_sensitivity=item.price_sensitivity,
            research_level=item.research_level,
            decision_time=item.decision_time,

            pain_points=item.pain_points,
            motivations=item.motivations,
            buying_triggers=item.buying_triggers,
            objections=item.objections,

            message_angles=item.message_angles,
            marketing_channels=item.marketing_channels,
        )


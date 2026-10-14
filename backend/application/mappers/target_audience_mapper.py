from domain.models.audience.target_audience import TargetAudience
from application.dtos.audience.target_audience_dto import TargetAudienceDto


class TargetAudienceMapper:

    @staticmethod
    def to_dto(item: TargetAudience) -> TargetAudienceDto:
        return TargetAudienceDto(
            id=item.id,
            offer_profile_id=item.offer_profile_id,
            fact_status=item.fact_status,
            is_reviewed=item.is_reviewed,

            name=item.name,


            age_min=item.age_min,
            age_max=item.age_max,
            gender=item.gender,

            lifestyles=item.lifestyles,
            values=item.values,


            pain_points=item.pain_points,
            motivations=item.motivations,
            buying_triggers=item.buying_triggers,
            desires=item.desires,

        )


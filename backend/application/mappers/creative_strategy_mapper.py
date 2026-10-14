from domain.models.creative.creative_strategy import CreativeStrategy
from application.dtos.creative_strategy.creative_strategy_response_dto import CreativeStrategyDto


class CreativeStrategyMapper:

    @staticmethod
    def to_dto(item: CreativeStrategy) -> CreativeStrategyDto:
        return CreativeStrategyDto(
            id=item.id,
            ad_strategy_id=item.ad_strategy_id,
            name=item.name,
            objective=item.objective,
            creative_type=item.creative_type,
            recommended_format=item.recommended_format,
            target=item.target,
            creative_big_idea=item.creative_big_idea,
            message_angle=item.message_angle,
            hook_strategy=item.hook_strategy,
            emotion_flow=item.emotion_flow,
            proof_strategy=item.proof_strategy,
        )

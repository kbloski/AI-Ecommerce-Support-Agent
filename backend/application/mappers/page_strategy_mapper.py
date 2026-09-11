from domain.models.page_strategy.page_strategy import PageStrategy
from application.dtos.page_strategy.page_strategy_response_dto import PageStrategyDto


class PageStrategyMapper:

    @staticmethod
    def to_dto(item: PageStrategy) -> PageStrategyDto:
        return PageStrategyDto(
            id=item.id,
            message_strategy_id=item.message_strategy_id,
            name=item.name,
            goal=item.goal,
            conversion_action=item.conversion_action,
            target_audience=item.target_audience,
            customer_awareness_level=item.customer_awareness_level,
            customer_journey_stage=item.customer_journey_stage,
            core_value_proposition=item.core_value_proposition,
            main_message=item.main_message,
            message_angle=item.message_angle,
            customer_problem=item.customer_problem,
            customer_desire=item.customer_desire,
            emotional_drivers=item.emotional_drivers,
            rational_drivers=item.rational_drivers,
            purchase_motivators=item.purchase_motivators,
            purchase_barriers=item.purchase_barriers,
            objections_to_resolve=item.objections_to_resolve,
            trust_requirements=item.trust_requirements,
            competitive_positioning=item.competitive_positioning,
            brand_voice_direction=item.brand_voice_direction,
            conversion_strategy=item.conversion_strategy,
            customer_journey_strategy=item.customer_journey_strategy,
        )

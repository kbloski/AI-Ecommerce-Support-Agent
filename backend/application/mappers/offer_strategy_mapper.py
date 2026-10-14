from domain.models.offer.offer_strategy import OfferStrategy
from application.dtos.offer_strategy.offer_strategy_response_dto import OfferStrategyDto


class OfferStrategyMapper:

    @staticmethod
    def to_dto(item: OfferStrategy) -> OfferStrategyDto:
        return OfferStrategyDto(
            id=item.id,
            marketing_strategy_id=item.marketing_strategy_id,
            offer_name=item.offer_name,
            offer_positioning=item.offer_positioning,
            core_value_proposition=item.core_value_proposition,
            main_customer_problem=item.main_customer_problem,
            solution_mechanism=item.solution_mechanism,
            primary_benefit=item.primary_benefit,
            secondary_benefits=item.secondary_benefits,
            functional_benefits=item.functional_benefits,
            emotional_benefits=item.emotional_benefits,
            offer_structure=item.offer_structure,
            value_stack=item.value_stack,
            risk_reversal=item.risk_reversal,
            trust_elements=item.trust_elements,
            pricing_strategy=item.pricing_strategy,
            urgency_strategy=item.urgency_strategy,
            customer_objection_handling=item.customer_objection_handling,
            competitive_difference=item.competitive_difference,
            conversion_levers=item.conversion_levers,
        )

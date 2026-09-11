from domain.models.ad_setup.ad_setup import AdSetup
from application.dtos.ad_setup.ad_setup_response_dto import AdSetupDto


class AdSetupMapper:

    @staticmethod
    def to_dto(item: AdSetup) -> AdSetupDto:
        return AdSetupDto(
            id=item.id,
            creative_strategy_id=item.creative_strategy_id,
            name=item.name,
            creative_type=item.creative_type,
            platform=item.platform,
            format=item.format,
        )

from domain.models.generate_ad.generate_ad import GenerateAd
from application.dtos.generate_ad.generate_ad_response_dto import GenerateAdDto


class GenerateAdMapper:

    @staticmethod
    def to_dto(item: GenerateAd) -> GenerateAdDto:
        return GenerateAdDto(
            id=item.id,
            creative_execution_setup_id=item.creative_execution_setup_id,
            name=item.name,
            content_json=item.content_json,
        )

from di.container import Container
from domain.models.analysis.analysis import Analysis
from domain.models.analysis.offer_profile_analysis import OfferProfileAnalysis
from application.mappers.analysis_mapper import AnalysisMapper
from infrastructure.database.unit_of_work import unit_of_work

def create_analysis_for_offer_profile_handler(offer_profile_id: int):
    container = Container()
    analysis_repository = container.analysis_repository()
    offer_profile_analysis_repotistory = container.offer_profile_analysis_repository()

    with unit_of_work(container.db()):
        new_analysis = Analysis()
        new_analysis = analysis_repository.create(new_analysis)

        new_offer_profile_analysis = OfferProfileAnalysis(
            offer_profile_id=offer_profile_id,
            analysis_id=new_analysis.id
        )

        offer_profile_analysis_repotistory.upsert(new_offer_profile_analysis)

    return AnalysisMapper.to_dto(new_analysis)
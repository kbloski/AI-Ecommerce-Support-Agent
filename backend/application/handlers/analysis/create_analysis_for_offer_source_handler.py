from di.container import Container
from domain.models.analysis.analysis import Analysis
from domain.models.analysis.offer_source_analysis import OfferSourceAnalysis
from application.mappers.analysis_mapper import AnalysisMapper
from infrastructure.database.unit_of_work import unit_of_work

def create_analysis_for_offer_source_handler(offer_source_id: int):
    container = Container()
    analysis_repository = container.analysis_repository()
    offer_source_analysis_repotistory = container.offer_source_analysis_repository()

    with unit_of_work(container.db()):
        new_analysis = Analysis()
        new_analysis = analysis_repository.create(new_analysis)

        new_offer_source_analysis = OfferSourceAnalysis(
            offer_source_id=offer_source_id,
            analysis_id=new_analysis.id
        )

        offer_source_analysis_repotistory.upsert(new_offer_source_analysis)

    return AnalysisMapper.to_dto(new_analysis)
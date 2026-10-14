from di.container import Container
from application.mappers.analysis_mapper import AnalysisMapper

def get_analysis_for_offer_source_handler(offer_source_id : int):
    container = Container()

    offer_source_analysis_repository = container.offer_source_analysis_repository()
    analysis_repository = container.analysis_repository()

    offer_source_analysis_db = offer_source_analysis_repository.find_by_offer_source_id(offer_source_id=offer_source_id)
    offer_source_analysis_ids = [k.analysis_id for k in offer_source_analysis_db]

    analysis_db = analysis_repository.get_by_ids(ids=offer_source_analysis_ids)
    analysis_dtos = [AnalysisMapper.to_dto(a) for a in analysis_db]

    return analysis_dtos
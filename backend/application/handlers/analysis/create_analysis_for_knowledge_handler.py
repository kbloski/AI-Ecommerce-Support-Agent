from di.container import Container
from domain.models.analysis.analysis import Analysis
from domain.models.analysis.knowledge_analysis import KnowledgeAnalysis
from application.mappers.analysis_mapper import AnalysisMapper
from infrastructure.database.unit_of_work import unit_of_work

def create_analysis_for_knowledge_handler(knowledge_id: int):
    container = Container()
    analysis_repository = container.analysis_repository()
    knowledge_analysis_repotistory = container.knowledge_analysis_repository()

    with unit_of_work(container.db()):
        new_analysis = Analysis()
        new_analysis = analysis_repository.create(new_analysis)

        new_knowledge_analysis = KnowledgeAnalysis(
            knowledge_id=knowledge_id,
            analysis_id=new_analysis.id
        )

        knowledge_analysis_repotistory.upsert(new_knowledge_analysis)

    return AnalysisMapper.to_dto(new_analysis)
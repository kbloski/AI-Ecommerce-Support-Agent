from di.container import Container
from domain.models.analysis.analysis_checklist import AnalysisChecklist
from domain.models.checklist.checklist import Checklist
from application.mappers.checklist_mapper import ChecklistMapper
from infrastructure.database.unit_of_work import unit_of_work

def create_checklist_for_analysis_handler(analysis_id: int):
    container = Container()

    checklist_repository = container.checklist_repository()
    analysis_checklist_repository = container.analysis_checklist_repository()

    with unit_of_work(container.db()):
        checklist = Checklist(name="analysis_checklist")
        checklist_db = checklist_repository.create(checklist)

        analysis_checklist = AnalysisChecklist(checklist_id=checklist_db.id, analysis_id=analysis_id)
        analysis_checklist_repository.upsert(item=analysis_checklist)

    return ChecklistMapper.to_dto(item=checklist_db)
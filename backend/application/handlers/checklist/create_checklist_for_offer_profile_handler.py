from di.container import Container
from domain.models.checklist.checklist import Checklist
from application.mappers.checklist_mapper import ChecklistMapper
from infrastructure.database.unit_of_work import unit_of_work


def create_checklist_for_offer_profile_handler(offer_profile_id: int):
    container = Container()
    checklist_repository = container.checklist_repository()

    with unit_of_work(container.db()):
        checklist = Checklist(offer_profile_id=offer_profile_id, name="checklist")
        checklist_db = checklist_repository.create(checklist)

    return ChecklistMapper.to_dto(item=checklist_db)

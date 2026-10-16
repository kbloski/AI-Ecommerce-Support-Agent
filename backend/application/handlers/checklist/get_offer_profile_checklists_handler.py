from di.container import Container
from application.mappers.checklist_mapper import ChecklistMapper


def get_offer_profile_checklists_handler(offer_profile_id: int):
    container = Container()
    container.offer_profile_service().get_offer_profile_details_by_id(offer_profile_id)
    checklist_repository = container.checklist_repository()
    checklists_db = checklist_repository.find_for_offer_profile(offer_profile_id=offer_profile_id)
    return [ChecklistMapper.to_dto(item=checklist) for checklist in checklists_db]

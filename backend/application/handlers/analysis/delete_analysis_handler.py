from di.container import Container


def delete_analysis_handler(id: int):
    container = Container()
    analysis_repository = container.analysis_repository()
    analysis_questions_repository = container.analysis_questions_repository()
    offer_profile_analysis_repository = container.offer_profile_analysis_repository()

    analysis_questions_repository.delete_by_analysis_id(analysis_id=id)

    offer_profile_analysis_repository.delete_by_analysis_id(analysis_id=id)

    deleted = analysis_repository.delete(id=id)

    return {"deleted": deleted}

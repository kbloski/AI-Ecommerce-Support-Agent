from di.container import Container


def update_analysis_question_handler(id: int, fields: dict):
    container = Container()
    repository = container.analysis_questions_repository()
    question = repository.get_by_id(id)
    if question is None:
        raise LookupError(f"AnalysisQuestion with id {id} not found")

    if "is_reviewed" in fields:
        question.is_reviewed = fields["is_reviewed"]
        container.db().commit()
        container.db().refresh(question)

    return {"id": question.id, "is_reviewed": question.is_reviewed}

from di.container import Container
from application.mappers.analysis_question_mapper import AnalysisQuestionMapper


def list_analysis_questions_handler(
    analysis_id: int,
    page: int = 1,
    page_size: int = 20,
    is_reviewed: bool | None = None,
    sort: str = "unreviewed_first",
) -> dict:
    container = Container()
    questions_repository = container.analysis_questions_repository()
    answers_repository = container.question_answer_repository()
    result = questions_repository.search_for_analysis(analysis_id, page, page_size, is_reviewed, sort)
    answers_by_id = {answer.id: answer for answer in answers_repository.get_by_ids([item.question_answer_id for item in result.items])}
    return result.to_dict(lambda item: AnalysisQuestionMapper.to_dto(item, answers_by_id[item.question_answer_id]).to_dict())

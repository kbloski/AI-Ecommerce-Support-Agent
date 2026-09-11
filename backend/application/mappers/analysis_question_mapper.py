from domain.models.analysis.analysis_questions import AnalysisQuestion
from domain.models.analysis.question_answer import QuestionAnswer
from application.dtos.analysis.analysis_question_dto import AnalysisQuestionDto


class AnalysisQuestionMapper:

    @staticmethod
    def to_dto(analysis_question: AnalysisQuestion, question_answer: QuestionAnswer) -> AnalysisQuestionDto:
        return AnalysisQuestionDto(
            id=analysis_question.id,
            analysis_id=analysis_question.analysis_id,
            question_answer_id=question_answer.id,
            question=question_answer.question,
            answer=question_answer.answer,
            score=question_answer.score,
            confidence=question_answer.confidence,
            is_reviewed=analysis_question.is_reviewed,
        )

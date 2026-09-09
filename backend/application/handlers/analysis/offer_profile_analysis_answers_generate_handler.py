

import json
from typing import Dict, Any, List

from di.container import Container

from application.mappers.offer_profile_mapper import OfferProfileMapper
from application.mappers.analysis_question_mapper import AnalysisQuestionMapper

from domain.models.analysis.analysis_questions import AnalysisQuestion
from domain.models.analysis.question_answer import QuestionAnswer
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole
from domain.analysis.offer_profile_analysis_questions import OFFER_PROFILE_ANALYSIS_QUESTIONS

BASE_SYSTEM_PROMPT = """
You are an expert in e-commerce product analysis.

Your task is to analyze products in terms of their sales potential.
Think like an entrepreneur investing their own money into a product.

Rules:
1. Provide specific and factual answers.
2. Do not invent information that is not present in the data.
3. If information is missing, clearly state that fact.
4. Evaluate the product objectively.
5. Point out both advantages and risks.
"""



def chunk_list(
    items: List[str],
    size: int
) -> List[List[str]]:

    return [
        items[i:i + size]
        for i in range(0, len(items), size)
    ]


def build_product_context_prompt(
    product_data: Dict[str, Any]
) -> str:

    return f"""
PRODUCT DATA:

{json.dumps(
    product_data,
    ensure_ascii=False,
    indent=2
)}

Analyze the product based on the data provided above.
Do not draw conclusions based on information that is not present in the data.
"""


def build_questions_prompt(
    questions: List[str]
) -> str:

    return f"""
ANALYSIS QUESTIONS:

{json.dumps(
    questions,
    ensure_ascii=False,
    indent=2
)}


Answer each question based only on the provided product data.

Return ONLY valid JSON:

[
    {{
        "question": "exact question text",
        "answer": "detailed answer",
        "score" : 68,
        "confidence" : 0.87
    }}
]


Rules:
- Answer every question.
- Do not skip questions.
- Do not add markdown.
- Do not add any text outside JSON.
- If information is missing, state that clearly.
- JSON values must be written in English.
"""


def offer_profile_analysis_answers_generate_handler(
    offer_profile_id: int,
    analyse_id: int
) -> Dict[str, Any]:

    container = Container()
    logger = container.logger()
    offer_profile_service = container.offer_profile_service()
    ai_service = container.ai_service()
    offer_profile_analysis_repository = container.offer_profile_analysis_repository()
    analysis_repository = container.analysis_repository()
    analysis_questions_repository = container.analysis_questions_repository()
    question_answer_repository = container.question_answer_repository()

    # Get analysis
    offer_profile_analysis_db = offer_profile_analysis_repository.find_relation(offer_profile_id=offer_profile_id,analysis_id=analyse_id)
    analyse_db = analysis_repository.get_by_id(id=offer_profile_analysis_db.analysis_id)

    logger.info(f"Generating offer_profile analysis for offer_profile_id={offer_profile_id}")
    assembled_dto = offer_profile_service.get_offer_profile_details_by_id(offer_profile_id=offer_profile_id)
    offer_profile_json = assembled_dto.to_dict()

    question_batches = chunk_list(items=OFFER_PROFILE_ANALYSIS_QUESTIONS,size=10)

    logger.info(f"Split {len(OFFER_PROFILE_ANALYSIS_QUESTIONS)} questions into {len(question_batches)} batches")


    final_analysis_questions_dicts = []
    for batch_index, batch in enumerate(question_batches, start=1):

        logger.info(f"Processing batch {batch_index}/{len(question_batches)} ({len(batch)} questions)")

        messages = [
            LlmMessage(
                role=LlmMessageRole.SYSTEM,
                content=BASE_SYSTEM_PROMPT
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=build_product_context_prompt(
                    offer_profile_json
                )
            ),
            LlmMessage(
                role=LlmMessageRole.USER,
                content=build_questions_prompt(
                    questions=batch
                )
            )
        ]


        response = ai_service.chat_llm( messages=messages )
        batch_result = json.loads( response.content )



        logger.info(f"Batch {batch_index}/{len(question_batches)} returned {len(batch_result)} answers")
        final_analysis_questions_dicts.extend( batch_result  )

    logger.info(f"OfferProfile analysis completed for offer_profile_id={offer_profile_id}, total_answers={len(final_analysis_questions_dicts)}")


    # QuestionAnswer insert to db
    question_answers = [ QuestionAnswer(
        question=a["question"],
        answer=a["answer"],
        score=a["score"],
        confidence=a["confidence"]
    ) for a in final_analysis_questions_dicts]

    question_answers_db = question_answer_repository.create_many(items=question_answers)

    # AnalysisQuestion (link) insert to db
    analysis_questions = [ AnalysisQuestion(
        analysis_id=analyse_db.id,
        question_answer_id=qa.id
    ) for qa in question_answers_db]

    analysis_questions_db = analysis_questions_repository.create_many(items=analysis_questions)

    analysis_questions_dtos = [
        AnalysisQuestionMapper.to_dto(aq, qa)
        for aq, qa in zip(analysis_questions_db, question_answers_db)
    ]

    return analysis_questions_dtos
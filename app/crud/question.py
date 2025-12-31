from sqlalchemy.orm import Session
from uuid import UUID
from app.models.question import Question, QuestionType
from app.models.question import Answer
from app.schemas.question import AnswerCreate, AnswerUpdate
from app.models.question import InfluencingQuestion
from app.schemas.question import (
    InfluencingQuestionCreate,
    InfluencingQuestionUpdate
)







def get_all_question_types(db: Session):
    return db.query(QuestionType).all()


def get_questions_by_type(db: Session, question_type_id: UUID):
    return db.query(Question).filter(
        Question.question_type_id == question_type_id
    ).all()






def create_answer(db: Session, data: AnswerCreate) -> Answer:
    answer = Answer(**data.model_dump())
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


def get_answers_for_book_user(db: Session, book_user_id: UUID):
    return db.query(Answer).filter(
        Answer.book_user_id == book_user_id
    ).all()


def update_answer(db: Session, answer: Answer, data: AnswerUpdate) -> Answer:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(answer, field, value)
    db.commit()
    db.refresh(answer)
    return answer





def create_influencing_question(db: Session, data: InfluencingQuestionCreate):
    iq = InfluencingQuestion(**data.model_dump())
    db.add(iq)
    db.commit()
    db.refresh(iq)
    return iq


def get_influencing_for_book_user(db: Session, book_user_id: UUID):
    return db.query(InfluencingQuestion).filter(
        InfluencingQuestion.book_user_id == book_user_id
    ).all()


def update_influencing_question(
    db: Session,
    iq: InfluencingQuestion,
    data: InfluencingQuestionUpdate
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(iq, field, value)
    db.commit()
    db.refresh(iq)
    return iq

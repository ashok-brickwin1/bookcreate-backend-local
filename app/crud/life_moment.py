from sqlalchemy.orm import Session
from uuid import UUID
from app.models.life_moment import LifeMoment
from app.schemas.life_moment import LifeMomentCreate
import logging
from typing import List

logger = logging.getLogger(__name__)


def create_life_moment(
    db: Session,
    data: LifeMomentCreate,
    book_user_id: UUID
) -> LifeMoment:
    logger.info(f"creating life moment for book_user_id:{book_user_id}")

    moment = LifeMoment(
        book_user_id=book_user_id,
        moment_type=data.moment_type,
        life_stage=data.life_stage,
        year=data.year,
        what_happened=data.what_happened,
        story=data.story,
        lesson_learned=data.lesson_learned,
    )

    db.add(moment)
    db.commit()
    db.refresh(moment)
    return moment




def bulk_create_life_moments(
    db: Session,
    moments: List[LifeMomentCreate],
    book_user_id: UUID
):
    logger.info(f"creating bulk moments with moments data:{moments}")
    objects = [
        LifeMoment(
            book_user_id=book_user_id,
            moment_type=m.moment_type,
            life_stage=m.life_stage,
            year=m.year,
            what_happened=m.what_happened,
            story=m.story,
            lesson_learned=m.lesson_learned,
        )
        for m in moments
    ]

    db.add_all(objects)
    db.commit()

    for obj in objects:
        db.refresh(obj)

    return objects

def list_life_moments(
    db: Session,
    book_user_id: UUID
):
    return (
        db.query(LifeMoment)
        .filter(LifeMoment.book_user_id == book_user_id)
        .order_by(LifeMoment.created_at.asc())
        .all()
    )


def delete_life_moment(
    db: Session,
    moment_id: UUID,
    book_user_id: UUID
):
    moment = (
        db.query(LifeMoment)
        .filter(
            LifeMoment.id == moment_id,
            LifeMoment.book_user_id == book_user_id
        )
        .first()
    )

    if not moment:
        return None

    db.delete(moment)
    db.commit()
    return moment

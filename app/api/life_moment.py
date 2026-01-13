from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.book_user import BookUser
from app.models.book import Book
from app.models.research import ResearchSource
from app.schemas.life_moment import LifeMomentCreate, LifeMomentRead,LifeMomentBulkCreate
from app.crud.life_moment import (
    create_life_moment,
    list_life_moments,
    delete_life_moment,
    bulk_create_life_moments
)
from app.api.book import run_conduct_research_worker
from fastapi import BackgroundTasks
import logging, secrets, string
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=LifeMomentRead,
    status_code=status.HTTP_201_CREATED
)
def add_life_moment(
    payload: LifeMomentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    try:

        
        logger.info(f"creating life moment with payload:{payload}")
        
        book_user = (
            db.query(BookUser)
            .filter(
                BookUser.user_id == current_user.id,
                BookUser.is_deleted == False
            )
            .order_by(BookUser.created_at.desc())
            .first()
        )

        if not book_user:
            logger.info("Book user not found")
            raise HTTPException(status_code=404, detail="Book user not found")

        return create_life_moment(
            db=db,
            data=payload,
            book_user_id=book_user.id
        )
    
    except Exception as e:
        logger.info(f"failed to create life moment:{str(e)}")
        return {
            "success": False
        }




@router.get("", response_model=list[LifeMomentRead])
def get_life_moments(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    book_user = (
        db.query(BookUser)
        .filter(
            BookUser.user_id == current_user.id,
            BookUser.is_deleted == False
        )
        .order_by(BookUser.created_at.desc())
        .first()
    )

    if not book_user:
        raise HTTPException(status_code=404, detail="Book user not found")

    return list_life_moments(db, book_user.id)


@router.delete("/{moment_id}", status_code=204)
def remove_life_moment(
    moment_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    book_user = (
        db.query(BookUser)
        .filter(
            BookUser.user_id == current_user.id,
            BookUser.is_deleted == False
        )
        .order_by(BookUser.created_at.desc())
        .first()
    )

    if not book_user:
        raise HTTPException(status_code=404, detail="Book user not found")

    deleted = delete_life_moment(db, moment_id, book_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Life moment not found")

    return None






@router.post(
    "/bulk/save",
    response_model=list[LifeMomentRead],
    status_code=status.HTTP_201_CREATED,
)
def bulk_add_life_moments(
    payload: LifeMomentBulkCreate,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Bulk creating life moments: count={len(payload.moments)}")

    book_user = (   
        db.query(BookUser)
        .filter(
            BookUser.user_id == current_user.id,
            BookUser.is_deleted == False
        )
        .order_by(BookUser.created_at.desc())
        .first()
    )

    book = (
        db.query(Book)
        .filter(
            Book.book_user_id == book_user.id
        )
        .order_by(Book.created_at.desc())
        .first()
    )

    if not book_user:
        logger.info("Book user not found at bulk create life moment")
        raise HTTPException(
            status_code=404,
            detail="Book user not found"
        )

    if not payload.moments:
        return []

    try:

        
        response=bulk_create_life_moments(
            db=db,
            moments=payload.moments,
            book_user_id=book_user.id
        )

        # background_tasks.add_task(
        #         run_conduct_research_worker,
        #         book.id
        #     )
        return response

    except Exception as e:
        logger.exception("Failed to bulk create life moments")
        raise HTTPException(
            status_code=500,
            detail="Failed to save life moments"
        )





dummy_bulk_life_moments = {
    "moments": [
        {
            "moment_type": "high",
            "life_stage": "foundations",
            "year": 1999,
            "what_happened": "Moved to a new city with my family",
            "story": "Leaving familiar surroundings was challenging, but it helped me adapt and build independence early on.",
            "lesson_learned": "Change, while uncomfortable, can be a powerful teacher."
        },
        {
            "moment_type": "low",
            "life_stage": "foundations",
            "year": 2004,
            "what_happened": "Struggled academically for the first time",
            "story": "Failing an important exam shook my confidence and forced me to rethink how I approached learning.",
            "lesson_learned": "Failure is feedback, not a verdict."
        },
        {
            "moment_type": "high",
            "life_stage": "growth",
            "year": 2013,
            "what_happened": "Took a major risk by changing my career path",
            "story": "Walking away from stability felt frightening, but it aligned my work with my interests.",
            "lesson_learned": "Growth requires courage and trust in yourself."
        },
        {
            "moment_type": "low",
            "life_stage": "growth",
            "year": 2016,
            "what_happened": "Experienced burnout for the first time",
            "story": "Pushing too hard without boundaries led to physical and emotional exhaustion.",
            "lesson_learned": "Sustainability matters more than speed."
        },
        {
            "moment_type": "high",
            "life_stage": "mastery",
            "year": 2021,
            "what_happened": "Led a team through a critical business transformation",
            "story": "Guiding others through uncertainty strengthened my leadership and communication skills.",
            "lesson_learned": "Leadership is about clarity, empathy, and trust."
        },
        {
            "moment_type": "high",
            "life_stage": "wisdom",
            "year": 2024,
            "what_happened": "Gained clarity on purpose and legacy",
            "story": "Reflecting on past experiences helped me understand what kind of impact I want to leave behind.",
            "lesson_learned": "Impact outlives achievement."
        }
    ]
}


@router.get(
    "/dummy/bulk",
    response_model=LifeMomentBulkCreate,
    status_code=status.HTTP_201_CREATED,
)
def bulk_add_life_moments(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Bulk creating dummy life moments")
    return dummy_bulk_life_moments


@router.get(
    "/get-bulk",
    response_model=LifeMomentBulkCreate,
    status_code=status.HTTP_201_CREATED,
)
def bulk_get_life_moments(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """get all life moments of logged in user to last created book user"""
    logger.info(f"Fetching bulk life moments for current user id:{current_user.id}")
    book_user = (   
        db.query(BookUser)
        .filter(
            BookUser.user_id == current_user.id,
            BookUser.is_deleted == False
        )
        .order_by(BookUser.created_at.desc())
        .first()
    )
    logger.info(f"Fetching bulk life moments for book user id:{book_user.id if book_user else 'not found'}")

    if not book_user:
        logger.info("Book user not found at bulk get life moment")
        raise HTTPException(
            status_code=404,
            detail="Book user not found"
        )

    moments = list_life_moments(db, book_user.id)

    if not moments:
        return {
            "moments": []
        }

    response_moments = []

    for m in moments:
        response_moments.append(
            LifeMomentCreate(
                moment_type=m.moment_type,
                life_stage=m.life_stage,
                year=m.year,
                what_happened=m.what_happened,
                story=m.story,
                lesson_learned=m.lesson_learned
            )
        )

    return {
        "moments": response_moments
    }
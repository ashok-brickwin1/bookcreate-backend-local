from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.book_user import BookUser
from app.models.book import Book
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

        background_tasks.add_task(
                run_conduct_research_worker,
                book.id
            )
        return response

    except Exception as e:
        logger.exception("Failed to bulk create life moments")
        raise HTTPException(
            status_code=500,
            detail="Failed to save life moments"
        )

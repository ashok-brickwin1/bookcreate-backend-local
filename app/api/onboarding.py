from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User
from app.api.deps import get_db,login_required, get_current_user
from app.schemas.onboarding import OnboardingSubmitSchema
from app.crud.onboarding import (
    save_influential_content,
    save_vision_answers
)
from app.schemas.book_user import BookUserCreate,BookUserRead
from app.crud.research import create_research_source,create_research_sources_from_social_profiles
from app.crud.book_user import create_book_user
import logging

# root logger
logger = logging.getLogger()

router = APIRouter()


@router.post("/submit", status_code=status.HTTP_201_CREATED)
def submit_onboarding(
    payload: OnboardingSubmitSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # 1️⃣ USER
        logger.info(f"payload on submit onboarding:{payload}")
        logger.info(f"current user which is making book is:{current_user}")
        

        # 2️⃣ BOOK USER
        book_user_data = BookUserCreate(
            user_id=current_user.id,
            name=payload.basic_info.full_name,
            email=payload.basic_info.email,
            title=payload.basic_info.role,
            bio=payload.basic_info.bio,
        )
        book_user = create_book_user(
            db=db,
            data=book_user_data
        )

        logger.info("book user created")

        # 3️⃣ INFLUENTIAL CONTENT
        save_influential_content(
            db=db,
            book_user_id=book_user.id,
            influential_content=payload.influential_content.model_dump(),
        )

        logger.info(f"saved influential content with data:{payload.influential_content}")

        # 4️⃣ VISION ANSWERS
        save_vision_answers(
            db=db,
            book_user_id=book_user.id,
            vision_answers=payload.vision_answers,
        )

        logger.info(f"saved vision answers with data:{payload.vision_answers}")


        # 4️⃣ RESEARCH SOURCES FROM SOCIAL PROFILES ✅
        create_research_sources_from_social_profiles(
            db=db,
            book_user_id=book_user.id,
            social_profiles=payload.social_profiles.model_dump(),
        )

        logger.info("Research sources created from social profiles")


        return {
            "success": True,
            "book_user_id": book_user.id,
            "message": "Onboarding completed successfully",
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error during onboarding: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}",
        )


# @router.post("/submit", status_code=status.HTTP_201_CREATED)
# def submit_onboarding(
#     payload: OnboardingSubmitSchema,
#     db: Session = Depends(get_db),
# ):
#     """
#     This endpoint receives the complete onboarding payload.
#     You can:
#     - Save it normalized (recommended)
#     - Save raw JSON (for AI pipelines)
#     - Or both
#     """

#     # ✅ For now, log / inspect
#     print("ONBOARDING PAYLOAD:")
#     print(payload.model_dump())

#     # TODO (next step):
#     # - Create BookUser
#     # - Save social profiles
#     # - Save influencing content
#     # - Save vision answers

    


    

#     return {
#         "success": True,
#         "message": "Onboarding data submitted successfully"
#     }

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
from app.models.research import ResearchSource
from app.schemas.book_user import BookUserCreate,BookUserRead
from app.crud.research import create_research_source,create_research_sources_from_social_profiles
from app.crud.book_user import create_book_user
from app.crud.vision import upsert_vision_answers
from app.crud.research import upsert_research_sources_from_social_profiles
import logging

from app.crud.onboarding import (
    save_influential_content,upsert_influential_content,
    save_vision_answers,get_influential_content_for_book_user
)
from app.schemas.book_user import BookUserCreate,BookUserRead
from app.crud.research import create_research_source,create_research_sources_from_social_profiles,get_social_profiles_for_book_user
from app.crud.book_user import create_book_user,get_latest_book_user
from app.crud.vision import get_vision_answers_for_book_user

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

        # check if have to new create or update existing book user
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




# @router.post("/modify", status_code=status.HTTP_201_CREATED)
# def submit_onboarding(
#     payload: OnboardingSubmitSchema,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     try:
#         return {
#             "success": True,
#             "book_user_id": "d86a6815-5c1f-4f6b-887b-c64366423fe1",
#             "message": "Onboarding completed successfully",
#         }
#         # 1️⃣ USER
#         logger.info(f"payload on submit onboarding:{payload}")
#         logger.info(f"current user which is making book is:{current_user}")
        

#         # 2️⃣ BOOK USER

        

#         book_user_data = BookUserCreate(
#             user_id=current_user.id,
#             name=payload.basic_info.full_name,
#             email=payload.basic_info.email,
#             title=payload.basic_info.role,
#             bio=payload.basic_info.bio,
#         )

#         # check if have to new create or update existing book user
#         book_user = create_book_user(
#             db=db,
#             data=book_user_data
#         )

#         logger.info("book user created")

#         # 3️⃣ INFLUENTIAL CONTENT
#         save_influential_content(
#             db=db,
#             book_user_id=book_user.id,
#             influential_content=payload.influential_content.model_dump(),
#         )

#         logger.info(f"saved influential content with data:{payload.influential_content}")

#         # 4️⃣ VISION ANSWERS
#         save_vision_answers(
#             db=db,
#             book_user_id=book_user.id,
#             vision_answers=payload.vision_answers,
#         )

#         logger.info(f"saved vision answers with data:{payload.vision_answers}")


#         # 4️⃣ RESEARCH SOURCES FROM SOCIAL PROFILES ✅
#         create_research_sources_from_social_profiles(
#             db=db,
#             book_user_id=book_user.id,
#             social_profiles=payload.social_profiles.model_dump(),
#         )

#         logger.info("Research sources created from social profiles")


#         return {
#             "success": True,
#             "book_user_id": book_user.id,
#             "message": "Onboarding completed successfully",
#         }

#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Database error during onboarding: {str(e)}",
#         )

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error: {str(e)}",
#         )

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



from uuid import uuid4

DUMMY_ONBOARDING_DATA = {
    "basic_info": {
        "full_name": "Ashwani Kumar",
        "email": "ashwani.kumar@example.com",
        "role": "Founder & Product Builder",
        "bio": "I build AI-driven products focused on storytelling, automation, and personal growth."
    },
    "social_profiles": {
        "linkedin": "https://linkedin.com/in/ashwanikumar",
        "twitter": "https://twitter.com/ashwani_ai",
        "website": "https://ashwani.dev",
        "others": {
            "github": "https://github.com/ashwani",
            "medium": "https://medium.com/@ashwani"
        }
    },
    "influential_content": {
        "personal": [
            {
                "type": "book",
                "title": "The Alchemist",
                "why": "It taught me to trust my journey and follow intuition."
            }
        ],
        "professional": [
            {
                "type": "podcast",
                "title": "Lex Fridman Podcast",
                "why": "Long-form conversations helped me think deeply about AI and humanity."
            }
        ],
        "curiosity": [
            {
                "type": "article",
                "title": "The Future of Artificial Intelligence",
                "why": "Sparked my interest in building ethical AI systems."
            }
        ],
        "legacy": [
            {
                "type": "speech",
                "title": "Steve Jobs – Stanford Commencement",
                "why": "Inspired me to focus on impact rather than titles."
            }
        ]
    },
    "vision_answers": [
        {
            "vision_question_id": uuid4(),
            "answer": "I see myself leading a small but impactful AI product company."
        },
        {
            "vision_question_id": uuid4(),
            "answer": "I want to master system design, applied AI, and leadership."
        }
    ]
}



# @router.get("/dummy", response_model=OnboardingSubmitSchema)
# def get_dummy_onboarding_data():
#     """
#     Returns dummy onboarding data for frontend hydration/testing
#     """
#     logger.info("Providing dummy onboarding data")
#     return {
#         "basic_info": {
#             "full_name": "Ashwani Kumar dfxscsd",
#             "email": "ashwani.kumar@example.com",
#             "role": "Founder & Product Builder",
#             "bio": "I build AI-driven products focused on storytelling, automation, and personal growth."
#         },
#         "social_profiles": {
#             "linkedin": "https://linkedin.com/in/ashwanikumar",
#             "twitter": "https://twitter.com/ashwani_ai",
#             "website": "https://ashwani.dev",
#             "others": {
#                 "github": "https://github.com/ashwani",
#                 "medium": "https://medium.com/@ashwani"
#             }
#         },
#         "influential_content": {
#             "personal": [
#                 {
#                     "type": "book",
#                     "title": "The Alchemist",
#                     "why": "It taught me to trust my journey and follow intuition."
#                 }
#             ],
#             "professional": [
#                 {
#                     "type": "podcast",
#                     "title": "Lex Fridman Podcast",
#                     "why": "Long-form conversations helped me think deeply about AI and humanity."
#                 }
#             ],
#             "curiosity": [
#                 {
#                     "type": "article",
#                     "title": "The Future of Artificial Intelligence",
#                     "why": "Sparked my interest in building ethical AI systems."
#                 }
#             ],
#             "legacy": [
#                 {
#                     "type": "speech",
#                     "title": "Steve Jobs – Stanford Commencement",
#                     "why": "Inspired me to focus on impact rather than titles."
#                 }
#             ]
#         },
#         "vision_answers": [
#             {
#                 "vision_question_id": "af35b8e5-609e-4e49-a323-288296440161",
#                 "answer": "I see myself leading a small but impactful AI product company."
#             },
#             {
#                 "vision_question_id": "ef148855-522f-4e6d-bd3f-3f2a3e8a0fe9",
#                 "answer": "I want to master system design, applied AI, and leadership."
#             }
#         ]
#     }




# @router.get("/dummy/empty", response_model=OnboardingSubmitSchema)
# def get_dummy_onboarding_data():
#     """
#     Returns dummy onboarding data for frontend hydration/testing
#     """
#     logger.info("Providing dummy onboarding data")
#     return {
#         "basic_info": {
#             "full_name": "",
#             "email": "abc@example.com",
#             "role": "",
#             "bio": ""
#         },
#         "social_profiles": {
#             "linkedin": "",
#             "twitter": "",
#             "website": "",
#             "others": {
                
#             }
#         },
    
#         "influential_content": {
#             "personal": [
                
#             ],
#             "professional": [
                
#             ],
#             "curiosity": [
                
#             ],
#             "legacy": [
                
#             ]
#         },
#         "vision_answers": [
#             {
#                 "vision_question_id": "af35b8e5-609e-4e49-a323-288296440161",
#                 "answer": ""
#             },
#             {
#                 "vision_question_id": "ef148855-522f-4e6d-bd3f-3f2a3e8a0fe9",
#                 "answer": ""
#             }
#         ]
#     }








@router.post("/modify")
def update_onboarding(
    payload: OnboardingSubmitSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    logger.info(f"payload on update onboarding:{payload}")
    logger.info(f"current user which is modifying book is:{current_user}")
    book_user = get_latest_book_user(db, current_user.id)

    if not book_user:
        raise HTTPException(404, "Book user not found")

    # update basic info
    book_user.name = payload.basic_info.full_name
    book_user.email = payload.basic_info.email
    book_user.title = payload.basic_info.role
    book_user.bio = payload.basic_info.bio

    # have to delete existing related data and re-insert new data 

    upsert_influential_content(db, book_user.id, payload.influential_content.model_dump())
    upsert_vision_answers(db, book_user.id, payload.vision_answers)
    
    # research_sources = db.query(ResearchSource).filter(
    #     ResearchSource.book_user_id == book_user.id
    # ).all()
    # logger.info(f"before deleting research sources:{research_sources}")
    db.query(ResearchSource).filter(
    ResearchSource.book_user_id == book_user.id
).delete(synchronize_session=False)

    db.commit()

    # db.delete(research_sources)

    # db.commit()

    upsert_research_sources_from_social_profiles(
        db, book_user.id, payload.social_profiles.model_dump()
    )

    # logger.info(f"after deleting research sources:{}")

    return {
            "success": True,
            "book_user_id": book_user.id,
            "message": "Onboarding completed successfully",
        }




@router.get("/dummy", response_model=OnboardingSubmitSchema)
def get_dummy_onboarding_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    """
    Returns dummy onboarding data for frontend hydration/testing
    """
    logger.info("Providing dummy onboarding data")
    print("TEST ASHOK1")
    
    print(current_user.id,"TEST ASHOK4")
    book_user = get_latest_book_user(db, current_user.id)
    basic_info = {
            "full_name": book_user.name,
            "email": book_user.email,
            "role": book_user.title,
            "bio": book_user.bio,
        }
    print(basic_info,"TEST ASHOK5")

    social_profiles = get_social_profiles_for_book_user(db, book_user.id)
    print(social_profiles,"TEST ASHOK6")

    influential_content = get_influential_content_for_book_user(db, book_user.id)
    print(influential_content,"TEST ASHOK7")


    vision_answers = get_vision_answers_for_book_user(db, book_user.id)
    print(vision_answers,"TEST ASHOK8")


    return {
        "basic_info": basic_info,
        "social_profiles": social_profiles,
        "influential_content": influential_content,
        "vision_answers": vision_answers,
    }

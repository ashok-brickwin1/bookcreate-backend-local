# app/api/book.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.book_user import BookUser
from app.models.research import ResearchSource
from app.schemas.book import BookSetupSubmitSchema, BookCreate,BookSetupRequest
from app.models.book import Book
from app.scripts.web_research import conduct_research,conduct_research_copy
from app.scripts.generate_outline import generate_outline_copy
from app.crud.book import create_book
import json
from uuid import UUID
from app.db.database import SessionLocal
from fastapi import BackgroundTasks
from app.core.utils import build_user_story_context
import logging
import time 
# root logger
logger = logging.getLogger()
router = APIRouter()




# def run_conduct_research_worker(book_user_id):
#     db = SessionLocal()  # ✅ NEW session (never reuse request DB session)
#     logger.info("worker started for research")

#     book=(
#         db.query(Book)
#         .filter(
#             Book.book_user_id == book_user_id
#         )
#         .first()
#     )

    

#     book_user = (
#         db.query(BookUser)
#         .filter(
#             BookUser.id == book_user_id,
#             BookUser.is_deleted == False
#         )
#         .order_by(BookUser.created_at.desc())
#         .first()
#     )
#     research_sources: list[str] = (
#     db.query(ResearchSource.source_url)
#     .filter(ResearchSource.book_user_id == book_user_id)
#     .all()
# )
    
#     research_sources = list({
#     url[0]
#     for url in research_sources
#     if url
# })
    
#     logger.info(f"research sources:{research_sources}")


#     search_results={"a":"asdf"}
#     logger.info(f"book id:{book.id}")
#     # search_results=conduct_research(figure_name=figure_name,research_sources=research_sources)
#     time.sleep(20) 
    
#     logger.info(f"search results:{search_results}")

#     book_user.digital_footprint_summary=search_results
#     book.raw_outline_json=search_results
#     book.status="outline_ready"
#     db.commit()
#     logger.info("digital footprint saved for book user")
#     logger.info("worker end for research")


def run_conduct_research_worker(book_id: UUID):
    db = SessionLocal()
    try:
        logger.info("🔄 Research worker started")

        # 1️⃣ Load Book
        book = (
            db.query(Book)
            .filter(Book.id == book_id, Book.is_deleted == False)
            .first()
        )

        if not book:
            logger.error("❌ Book not found in worker")
            return

        # 2️⃣ Load BookUser
        book_user = (
            db.query(BookUser)
            .filter(BookUser.id == book.book_user_id, BookUser.is_deleted == False)
            .first()
        )

        if not book_user:
            logger.error("❌ BookUser not found in worker")
            return

        # 3️⃣ Load research sources
        research_sources = (
            db.query(ResearchSource.source_url)
            .filter(ResearchSource.book_user_id == book_user.id)
            .all()
        )

        research_sources = list({url[0] for url in research_sources if url})

        logger.info(f"🔍 Research sources: {research_sources}")
        figure_name=book_user.name+" "+book_user.title
        logger.info(f"figure name :{figure_name}")


        answers_life_moments_context=build_user_story_context(db,book_user_id=book_user.id)
        logger.info(f"build_user_story_context :{answers_life_moments_context}")

        # ⏳ Simulate research
        # search_results=conduct_research_copy(figure_name=figure_name,context=answers_life_moments_context,research_sources=research_sources)
        time.sleep(20)
        

        search_results = json.dumps({"A":"v"})

        # 4️⃣ Update DB
        book_user.digital_footprint_summary = search_results
        

        

        logger.info(f"✅ Research completed for book {book.id}")


        # handle create book outline 
        # outline=generate_outline_copy(no_of_chapters=book.number_of_chapters)

        # book.raw_outline_json = outline
        book.status = "outline_ready"

        logger.info("outline genereated")


        # handle expand chapter using outline 




        db.commit()
        db.refresh(book)  # ✅ CRITICAL
        db.refresh(book_user)

    except Exception as e:
        db.rollback()
        # book.status = "failed"
        db.commit()
        db.refresh(book)
        logger.exception("🔥 Worker failed")
    finally:
        db.close()  # ✅ VERY IMPORTANT

    
@router.get("/status/{book_id}", status_code=200)
def check_book_status(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    try:

        logger.info(f"check_book_status called for book_id:{book_id}")
        book = (
            db.query(Book)
            .join(BookUser, Book.book_user_id == BookUser.id)
            .filter(
                Book.id == book_id,
                BookUser.user_id == current_user.id,
                Book.is_deleted == False
            )
            .first()
        )

        if not book:
            logger.info("book not found at status check api")
            raise HTTPException(status_code=404, detail="Book not found")
        


        return {
            "success": True,
            "book_id": book.id,
            "status": book.status
        }
    
    except Exception as e:
        logger.info(f"failed to check status:{str(e)}")
        return {
            "success": False
        }





@router.get("/research-data/{book_id}", status_code=status.HTTP_200_OK)
def get_research_data(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    try:

        # 1️⃣ Fetch Book
        book = (
            db.query(Book)
            .filter(
                Book.id == book_id,
                Book.is_deleted == False
            )
            .first()
        )

        if not book:
            logger.info("book not found at get_research_data ")
            raise HTTPException(status_code=404, detail="Book not found")

        # 2️⃣ Fetch BookUser (ownership check)
        book_user = (
            db.query(BookUser)
            .filter(
                BookUser.id == book.book_user_id,
                BookUser.user_id == current_user.id,
                BookUser.is_deleted == False
            )
            .first()
        )

        if not book_user:
            logger.info("book user not found at get_research_data")
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this book",
            )

        # 3️⃣ Return research data
        return {
            "success": True,
            "book_id": book.id,
            "book_user_id": book_user.id,
            "research_data": book.raw_outline_json,
        }
    

    except Exception as e:
        logger.info(f"failed to get research data:{str(e)}")
        return {
            "success": False
        }



        

    



@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_book_from_setup(
    payload: BookSetupRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    try:

        # 1️⃣ Fetch BookUser
        logger.info(f"payload at crete book setup:{payload}")
        book_setup = payload.book_setup
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

        # 2️⃣ Resolve genre
        genre = (
            book_setup.custom_genre.strip()
            if book_setup.genre == "custom" and book_setup.custom_genre
            else book_setup.genre
        )

        logger.info(f"genre:{genre}")

        # 3️⃣ Create Book
        book = create_book(
            db=db,
            data=BookCreate(
                book_user_id=book_user.id,
                genre=genre,
                title=book_setup.working_title,
                dedication=book_setup.dedication,
                number_of_chapters=book_setup.chapter_count,
                length_type=book_setup.desired_length,
            )
        )
        logger.info("book created")
        # [lib, 1,nfsd.]

        figure_name=book_user.name+" "+book_user.title
        logger.info(f"figure name :{figure_name}")

    #     research_sources = (
    #     db.query(
    #         ResearchSource.source_site,
    #         ResearchSource.source_url
    #     )
    #     .join(BookUser, ResearchSource.book_user_id == BookUser.id)
    #     .filter(BookUser.user_id == book_user.id)
    #     .order_by(BookUser.created_at.desc())
    #     .all()
    # )


    #     research_sources = (
    #     db.query(
    #         ResearchSource.source_url
    #     )
    #     .filter(ResearchSource.book_user_id == book_user.id)
    #     .all()
    # )

        
        


        # background_tasks.add_task(
        #         run_conduct_research_worker,
        #         book.id
        #     )


        return {
            "success": True,
            "book_id": book.id,
            "status": book.status,
            "message": "Book created successfully",
        }
    

    except Exception as e:
        logger.info(f"failed to create book setup:{str(e)}")
        return {
            "success": False
        }


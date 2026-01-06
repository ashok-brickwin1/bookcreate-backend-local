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
from app.scripts.expand_all_chapters import expand_all_chapters_copy
from app.scripts.generate_outline import generate_outline_copy
from app.scripts.expand_all_chapters import extract_chapter_titles_from_outline,expand_chapter_copy
from app.core.utils import dummy_outline1,dummy_outline_json,create_book_pdf_from_md
from app.crud.book import create_book
from fastapi.responses import StreamingResponse
from app.core.utils import send_email
from pathlib import Path
from app.api.deps import get_db, get_current_user,login_required
import os

import json
from uuid import UUID
from app.db.database import SessionLocal
from fastapi import BackgroundTasks
from app.core.utils import build_user_story_context,build_chapter_summaries_from_outline

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
def normalize_outline(outline):
    if outline is None:
        return None
    if isinstance(outline, str):
        return json.loads(outline)
    if isinstance(outline, dict):
        return outline
    raise TypeError(f"Unexpected outline type: {type(outline)}")


def run_conduct_research_worker(book_id: UUID):
     
    db = SessionLocal()
    try:
        logger.info(f"🔄 Research worker started for book id:{book_id}")

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
        
        search_results=conduct_research_copy(figure_name=figure_name,refresh=True,research_sources=research_sources)
        time.sleep(20)

        # {"bio_content": "### Search 1: site:www.linkedin.com Narendra Modi PM of India\n\n**Narendra Modi, the Prime Minister of India, actively uses LinkedIn to share his thoughts on key initiatives, such as a recent post about his visit to a natural farming summit in Coimbatore (Kimburtur).** [1]\n\nIn the post, highlighted in a DD India YouTube video from December 3, 2025, Modi describes his impressions from the event, praising the integration of India's traditional knowledge with modern ecological principles for chemical-free crop cultivation using farm residues, mulching, and aeration. [1] He notes India's progress, including the government's National Mission on Natural Farming launched the previous year, which has connected hundreds of thousands of farmers (referred to as \"lacks,\" likely meaning lakhs or 100,000s) to sustainable practices, and links it to promoting Shree Anna millets. [1] Modi emphasizes women farmers' growing adoption, addresses challenges like soil degradation from chemical fertilizers and rising costs, and calls for collective action among farmers, scientists, entrepreneurs, and citizens. [1] He ends by inviting followers to share information on natural farming teams. [1]\n\nNo direct LinkedIn post link appears in the search results, but this YouTube coverage from India's public broadcaster DD India confirms Modi's LinkedIn activity on the topic. [1] The query specified site:www.linkedin.com, but results point to this referenced content rather than the page itself.\n\n", "media_content": "### Search 1: site:www.linkedin.com Narendra Modi PM of India interview OR talk OR speech OR TV OR television OR news\n\nNo LinkedIn posts or pages directly matching the query for Narendra Modi as PM of India discussing an **interview**, **talk**, **speech**, **TV**, **television**, or **news** appear in the search results.\n\nThe available results from DD India (December 3, 2025) cover a YouTube video and short where **PM Modi shared thoughts via a LinkedIn post** about his Coimbatore trip, focusing on **natural farming**, sustainable agriculture, regional development, innovation, environmental stewardship, and citizen engagement.[1][2] The video transcript quotes Modi's post, highlighting a summit in Kimbatur (likely Coimbatore area), India's National Mission on Natural Farming, links to Shree Anna (millets), women farmers' involvement, and a call to share examples of natural farming teams.[1] It emphasizes traditional knowledge, soil health via mulching and aeration, reducing chemical dependency, and addressing rising farming costs.[1]\n\n", "pub_content": "", "quote_content": "", "framework_content": "", "theme_content": "### Search 1: \"Narendra Modi PM of India\" values OR beliefs OR principles\n\nNarendra Modi's core **values, beliefs, and principles** as Prime Minister of India emphasize **inclusive development**, **self-reliance**, **welfare of the poor**, **constitutional values**, **spirituality**, and **pragmatic nationalism**, often rooted in philosophies like Integral Humanism and Hindu thought.[1][2][3]\n\n### Key Principles from Governance and Ideology\nThese are synthesized from analyses of his policies, speeches, and leadership style:\n- **Antyodaya and Garib Kalyan (Upliftment of the poorest and welfare of the poor)**: Prioritizing the welfare of the underprivileged, lifting 25 crore people above the poverty line through grassroots schemes, embodying a shift from self to others.[2][4]\n- **Swadeshi and self-reliance (Atmanirbhar Bharat)**: Promoting economic independence, \"Made in India,\" industrialization, private investment, and defense self-sufficiency while attracting foreign capital.[1][2]\n- **Sabka Saath, Sabka Vikas (Together with all, development for all)**: Inclusive growth with minimum government intervention, harmony with society/nature, and cultural rootedness in Indian ethos like Advaita Vedanta, rejecting Western models.[2]\n- **Upholding the Constitution**: Dedication to its noble values of equality, hope, dignity, and welfare state vision, enabling service from humble origins.[3][4]\n- **Spirituality and inclusiveness**: Respect for all faiths, Hindu philosophy of equality, multilateralism with Indian values, and global promotion of yoga for inner peace.[1][2]\n- **Pragmatism and technopopulism**: Enterprise-driven prosperity, digitalization, financial inclusion, education reforms emphasizing Indian knowledge systems, and reforms like new criminal laws.[1][2]\n- **National security and multipolarity**: Firm anti-terrorism stance, military upgrades, Quad partnerships, rejecting hegemony, and sovereignty respect.[1]\n- **Humility and people-first governance**: Humble behavior while striving for success, equality before law, serving the electorate over lobbies.[1][3]\n\n### Philosophical Foundations\nModi's approach draws from **Integral Humanism** by Deendayal Upadhyaya, integrating dharma, artha, kama, and moksha for holistic development.[2] Leadership analyses highlight modeling discipline, shared national vision (e.g., Vikas bhi Virasat bhi\u2014development with heritage), bold reforms, and celebrating citizen efforts.[5] Critics note ties to **Hindutva** (Hindu nationalism).[6]\n\nThese principles have shaped policies from 2014\u20132025, including welfare, infrastructure, and environmental initiatives, per official and analytical sources.[2][4]\n\n", "dossier_path": "static/research/Narendra Modi PM of India/dossier.md"}
        

        # search_results = json.dumps({"A":"v"})

        # 4️⃣ Update DB
        book_user.digital_footprint_summary = json.dumps(search_results)
        logger.info(f"✅ Research completed for book {book.id}")
        dossier_path=search_results.get("dossier_path")
        with open(dossier_path, "r", encoding="utf-8") as f:
           dossier_text = f.read()

        research_files = {
                "dossier.md": dossier_text
            }



        # handle create book outline 
        # outline=json.dumps(dummy_outline_json)
        outline=generate_outline_copy(figure_name=figure_name,research_files=research_files,context=answers_life_moments_context,no_of_chapters=book.number_of_chapters)
        if isinstance(outline, str):
            outline = json.loads(outline)


        logger.info(f"type of outline generated:{type(outline)}")
        logger.info(f"outline:{outline}")

        # book.raw_outline_json = build_chapter_summaries_from_outline(outline)
        # book.raw_outline_json=extract_chapter_titles_from_outline(outline)
        # logger.info(f"after extract_chapter_titles_from_outline:{book.raw_outline_json}")
        book.status = "outline_ready"
        book.raw_outline_json=outline

        logger.info("outline genereated")


        # handle expand chapter using outline 

        # generated_book=expand_all_chapters_copy(figure_name=figure_name,outline=outline)
        # pdf_path=f"static/book/{figure_name}.pdf"





        db.commit()
        db.refresh(book)  # ✅ CRITICAL
        db.refresh(book_user)

    except Exception as e:
        db.rollback()
        logger.error(f"🔥 EXCEPTION TYPE: {type(e)}")
        logger.error(f"🔥 EXCEPTION MESSAGE at run_conduct_research_worker: {str(e)}")
        book.status = "failed"
        db.commit()
        db.refresh(book)
        logger.exception("🔥 Worker failed")
    finally:
        db.close()  # ✅ VERY IMPORTANT







def run_create_book(book_id: UUID):
    db = SessionLocal()
    try:
        logger.info(f"🔄 Create Book worker started for book id:{book_id}")

        # 1️⃣ Load Book
        book = (
            db.query(Book)
            .filter(Book.id == book_id, Book.is_deleted == False)
            .first()
        )

        if not book:
            logger.error("❌ Book not found in worker run_create_book")
            return

        # 2️⃣ Load BookUser
        book_user = (
            db.query(BookUser)
            .filter(BookUser.id == book.book_user_id, BookUser.is_deleted == False)
            .first()
        )

        if not book_user:
            logger.error("❌ BookUser not found in worker run_create_book")
            return
        

    
        figure_name=book_user.name+" "+book_user.title
        logger.info(f"figure name :{figure_name}")


        # outline=book.raw_outline_json
        outline = normalize_outline(book.raw_outline_json)
        logger.info(f"outline at run_create_book:{outline}")
        # outline=dummy_outline_json


        # handle expand chapter using outline 

        generated_book=expand_all_chapters_copy(figure_name=figure_name,outline=outline)

        logger.info(f"book md files genereted for :{book_id}")
        book.status = "created"


        #create book pdf from md files
        figure_name = f"{book_user.name} {book_user.title}"
        book_dir = Path(f"static/book/{figure_name}")
        output_pdf = Path(f"static/book/{figure_name}.pdf")

        logger.info(f"📘 Generating PDF for: {figure_name}")

        # 4️⃣ Generate PDF (writes to disk)
        create_book_pdf_from_md(
            book_dir=str(book_dir),
            output_pdf=str(output_pdf)
        )


        # send email functionality

        body="Please find the attached pdf of your book"

        send_email("ashwani.tripathi@brickwin.com","Your Book Has Generated",body, pdf_path=output_pdf)
        db.commit()
        db.refresh(book)  # ✅ CRITICAL
        db.refresh(book_user)

    except Exception as e:
        db.rollback()
        logger.error(f"🔥 EXCEPTION TYPE: {type(e)}")
        logger.error(f"🔥 EXCEPTION MESSAGE at run_create_book: {str(e)}")
        book.status = "failed"
        db.commit()
        db.refresh(book)
        logger.exception("🔥 run_create_book Worker failed")
    finally:
        db.close()  # ✅ VERY IMPORTANT



# def run_conduct_research_worker_copy(book_id: UUID):
     
#     db = SessionLocal()
#     try:
#         time.sleep(20)
#         logger.info(f"🔄 Research worker started for book id:{book_id}")

#         # 1️⃣ Load Book
#         book = (
#             db.query(Book)
#             .filter(Book.id == book_id, Book.is_deleted == False)
#             .first()
#         )

#         if not book:
#             logger.error("❌ Book not found in worker")
#             return

#         # 2️⃣ Load BookUser
#         book_user = (
#             db.query(BookUser)
#             .filter(BookUser.id == book.book_user_id, BookUser.is_deleted == False)
#             .first()
#         )

#         if not book_user:
#             logger.error("❌ BookUser not found in worker")
#             return
        

        
        
#         book.status = "failed"

#         logger.info(f"updating status for book id:{book.id}")

#         db.commit()
#         fresh = (
#     db.query(Book.status)
#     .filter(Book.id == book_id)
#     .scalar()
# )

#         logger.error(f"🧪 DB VALUE AFTER COMMIT = {fresh}")
#         db.refresh(book)  # ✅ CRITICAL
        

#     except Exception as e:
#         logger.error(f"🔥 EXCEPTION TYPE: {type(e)}")
#         logger.error(f"🔥 EXCEPTION MESSAGE: {str(e)}")
#         logger.exception("🔥 FULL TRACE")

#         db.rollback()
#         logger.info(f"after fail updating status for book id:{book.id}")
#         book.status = "failed"
#         db.commit()
#         db.refresh(book)
#         logger.exception("🔥 Worker failed")
#     finally:
#         db.close()  # ✅ VERY IMPORTANT








  
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
        # book_id=UUID("0f842fb4-253e-48c5-b5e0-c2d8193e09e4")

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
        
        logger.info(f"get research data called for book:{book.id}")
        logger.info(f"sending research_data:{book.raw_outline_json}")

        # 3️⃣ Return research data
        return {
            "success": True,
            "book_id": book.id,
            "book_user_id": book_user.id,
            "research_data": json.dumps(book.raw_outline_json),
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
        logger.info(f"book created with id:{book.id}")
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




@router.post(
    "/create/outline/{book_id}",
    status_code=status.HTTP_201_CREATED,
)
def create_book_outline(
    book_id:UUID,
    background_tasks: BackgroundTasks,
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

    # book = (
    #     db.query(Book)
    #     .filter(
    #         Book.book_user_id == book_user.id
    #     )
    #     .order_by(Book.created_at.desc())
    #     .first()
    # )

    if not book_user:
        logger.info("Book user not found at bulk create life moment")
        raise HTTPException(
            status_code=404,
            detail="Book user not found"
        )

    try:

        background_tasks.add_task(
                run_conduct_research_worker,
                book_id
            )
        return {
            "status":"success"
        }

    except Exception as e:
        logger.exception("Failed to bulk create life moments")
        raise HTTPException(
            status_code=500,
            detail="Failed to save life moments"
        )





@router.post(
    "/pdf/create/{book_id}",
    status_code=status.HTTP_201_CREATED,
)
def create_book_pdf(
    book_id:UUID,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    

    

    try:

        logger.info("create_book_pdf api called")
        # return {
        #     "status":"success"
        # }

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
            logger.info("Book user not found at bulk create life moment")
            raise HTTPException(
                status_code=404,
                detail="Book user not found"
            )

        background_tasks.add_task(
                run_create_book,
                book_id
            )
        return {
            "status":"success"
        }

    except Exception as e:
        logger.exception(f"Failed to create final book pdf:{str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create final book"
        )







# @router.post(
#     "/download/pdf/{book_id}",
#     status_code=status.HTTP_201_CREATED,
# )
# def download_book(
#     book_id:UUID,
#     current_user=Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):


#     try:
#         book_user = (   
#         db.query(BookUser)
#         .filter(
#             BookUser.user_id == current_user.id,
#             BookUser.is_deleted == False
#         )
#         .order_by(BookUser.created_at.desc())
#         .first()
#     )

#         book = (
#             db.query(Book)
#             .filter(Book.id == book_id, Book.is_deleted == False)
#             .first()
#         )


#         book_user = (   
#         db.query(BookUser)
#         .filter(
#             BookUser.user_id == book.book_user_id,
#             BookUser.is_deleted == False
#         )
#         .order_by(BookUser.created_at.desc())
#         .first()
#     )

#         figure_name=book_user.name+" "+book_user.title
#         logger.info(f"figure name :{figure_name}")
#         book_dir=f"static/book/{figure_name}"
#         output_pdf=f"static/book/{figure_name}.pdf"
#         # "static/book/Jeffrey Preston Bezos founder, executive chairman, and former president and CEO of Amazon"


#         create_book_pdf(
#     book_dir=book_dir,
#     output_pdf=output_pdf
# )
        


#     except Exception as e:
#         logger.exception(f"Failed to download book:{str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to download boook"
#         )







@router.post(
    "/download/pdf/{book_id}",
    status_code=status.HTTP_200_OK,
)
def download_book(
    book_id: UUID,
    current_user=Depends(login_required),
    db: Session = Depends(get_db),
):
    try:
        # 1️⃣ Fetch book
        book = (
            db.query(Book)
            .filter(Book.id == book_id, Book.is_deleted == False)
            .first()
        )

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        # 2️⃣ Fetch book user
        book_user = (
            db.query(BookUser)
            .filter(
                BookUser.id == book.book_user_id,
                BookUser.is_deleted == False
            )
            .first()
        )

        if not book_user:
            raise HTTPException(status_code=404, detail="Book user not found")

        # 3️⃣ Build paths
        figure_name = f"{book_user.name} {book_user.title}"
        book_dir = Path(f"static/book/{figure_name}")
        output_pdf = Path(f"static/book/{figure_name}.pdf")

        logger.info(f"📘 Generating PDF for: {figure_name}")

        # 4️⃣ Generate PDF (writes to disk)
        create_book_pdf_from_md(
            book_dir=str(book_dir),
            output_pdf=str(output_pdf)
        )

        # 5️⃣ Validate PDF exists
        if not output_pdf.exists():
            raise HTTPException(
                status_code=500,
                detail="PDF generation failed"
            )

        # 6️⃣ Stream PDF
        pdf_file = open(output_pdf, "rb")

        return StreamingResponse(
            pdf_file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{output_pdf.name}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Failed to download book PDF")
        raise HTTPException(
            status_code=500,
            detail="Failed to download book"
        )

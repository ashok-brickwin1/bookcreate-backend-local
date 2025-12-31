# from fastapi import APIRouter
# from uuid import UUID
# from app.services.research_engine import run_research

# router = APIRouter(
#     prefix="/projects",
#     tags=["Research"]
# )

# @router.post("/{project_id}/research")
# def start_research(project_id: UUID):
#     run_research(project_id)
#     return {"status": "research started"}


from sqlalchemy.orm import Session
from uuid import UUID
from app.models.research import ResearchSource
from app.schemas.research import ResearchSourceCreate, ResearchSourceUpdate
import logging

# root logger
logger = logging.getLogger()


def create_research_source(db: Session, data: ResearchSourceCreate):
    source = ResearchSource(**data.model_dump())
    db.add(source)
    return source


def get_research_sources(db: Session, book_user_id: UUID):
    return db.query(ResearchSource).filter(
        ResearchSource.book_user_id == book_user_id
    ).all()


def update_research_source(
    db: Session,
    source: ResearchSource,
    data: ResearchSourceUpdate
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(source, field, value)
    db.commit()
    db.refresh(source)
    return source


from sqlalchemy.exc import SQLAlchemyError

def create_research_sources_from_social_profiles(
    db: Session,
    book_user_id,
    social_profiles: dict,
):
    logger.info(
        f"called to create research sources from social profiles with data:{social_profiles}"
    )

    try:
        # Known keys
        for site in ["linkedin", "twitter", "website"]:
            url = social_profiles.get(site)
            if url:
                create_research_source(
                    db=db,
                    data=ResearchSourceCreate(
                        book_user_id=book_user_id,
                        source_site=site,
                        source_url=url,
                    ),
                )

        # Dynamic others
        others = social_profiles.get("others") or {}
        for site, url in others.items():
            if url:
                create_research_source(
                    db=db,
                    data=ResearchSourceCreate(
                        book_user_id=book_user_id,
                        source_site=site,
                        source_url=url,
                    ),
                )

        # ✅ SINGLE commit
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Failed to create research sources")
        raise

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





KNOWN_SITES = {"linkedin", "twitter", "website"}

def get_social_profiles_for_book_user(
    db: Session,
    book_user_id,
) -> dict:
    rows = (
        db.query(ResearchSource)
        .filter(ResearchSource.book_user_id == book_user_id)
        .all()
    )

    social_profiles = {
        "linkedin": None,
        "twitter": None,
        "website": None,
        "others": {},
    }
    print(rows,"ASHOK ROWS")
    for row in rows:
        if not row.source_site or not row.source_url:
            continue

        site = row.source_site.lower().strip()

        if site in KNOWN_SITES:
            social_profiles[site] = row.source_url
        else:
            social_profiles["others"][site] = row.source_url

    # optional: remove empty others
    if not social_profiles["others"]:
        social_profiles["others"] = {}


    logger.info(f"fetched social profiles for book_user_id:{book_user_id} profiles:{social_profiles}")

    return social_profiles

#ASHOK ADDED THIS FOR CREATE AND UPDATE
def upsert_research_sources_from_social_profiles(
    db: Session,
    book_user_id: UUID,
    social_profiles: dict,
):
    
    logger.info(f"called to upsert research sources from social profiles with data:{social_profiles}")
    def upsert(site, url):
        existing = (
            db.query(ResearchSource)
            .filter(
                ResearchSource.book_user_id == book_user_id
            )
            .first()
        )
        # deleting existing and adding new to avoid complexity
        if existing:
            db.delete(existing)
            db.commit()

        # if existing:
        #     existing.source_url = url
        # else:
        db.add(
            ResearchSource(
                book_user_id=book_user_id,
                source_site=site,
                source_url=url,
            )
        )

    for site in ["linkedin", "twitter", "website"]:
        if social_profiles.get(site):
            upsert(site, social_profiles[site])

    for site, url in (social_profiles.get("others") or {}).items():
        if url:
            upsert(site, url)

    db.commit()

    existing = (
            db.query(ResearchSource)
            .filter(
                ResearchSource.book_user_id == book_user_id
            )
            .all()
        )
    logger.info(f"no of research sources created/updated from social profiles: {len(existing)}")

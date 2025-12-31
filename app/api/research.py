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



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.models.research import SourceSite,ResearchSource
from app.schemas.research import (
    SourceSiteCreate,
    SourceSiteUpdate,
    SourceSiteOut,
    ResearchSourceOut
)

router = APIRouter()


@router.post("/", response_model=SourceSiteOut, status_code=status.HTTP_201_CREATED)
def create_source_site(payload: SourceSiteCreate, db: Session = Depends(get_db)):
    site = SourceSite(**payload.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/", response_model=list[SourceSiteOut])
def list_source_sites(db: Session = Depends(get_db)):
    return db.query(SourceSite).order_by(SourceSite.created_at.desc()).all()


@router.put("/{site_id}", response_model=SourceSiteOut)
def update_source_site(
    site_id: UUID,
    payload: SourceSiteUpdate,
    db: Session = Depends(get_db),
):
    site = db.query(SourceSite).filter(SourceSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Source site not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(site, key, value)

    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source_site(site_id: UUID, db: Session = Depends(get_db)):
    site = db.query(SourceSite).filter(SourceSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Source site not found")

    db.delete(site)
    db.commit()






@router.get("/research-sources/list/all", response_model=list[ResearchSourceOut])
def list_research_sources(
    db: Session = Depends(get_db),
):
    return (
        db.query(ResearchSource)
        .order_by(ResearchSource.created_at.desc())
        .all()
    )


@router.get("/research-sources/list/{book_user_id}", response_model=list[ResearchSourceOut])
def list_research_sources(
    book_user_id: UUID,
    db: Session = Depends(get_db),
):
    return (
        db.query(ResearchSource)
        .filter(ResearchSource.book_user_id == book_user_id)
        .order_by(ResearchSource.created_at.desc())
        .all()
    )
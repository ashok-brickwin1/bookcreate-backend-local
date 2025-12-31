from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.project import ProjectCreate, ProjectResponse
from app.crud.project import create_project
from app.core.database import get_db

router = APIRouter(prefix="/projects")

@router.post("/", response_model=ProjectResponse)
def create(data: ProjectCreate, db: Session = Depends(get_db)):
    user_id = "mock-user-uuid"
    return create_project(db, user_id, data)

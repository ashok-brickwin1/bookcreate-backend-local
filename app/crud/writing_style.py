from sqlalchemy.orm import Session
from app.models.writing_style import Style
from app.schemas.writing_style import StyleCreate


def create_style(db: Session, data: StyleCreate):
    style = Style(**data.model_dump())
    db.add(style)
    db.commit()
    db.refresh(style)
    return style


def list_styles(db: Session):
    return db.query(Style).all()

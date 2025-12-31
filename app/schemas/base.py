from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # REQUIRED for SQLAlchemy

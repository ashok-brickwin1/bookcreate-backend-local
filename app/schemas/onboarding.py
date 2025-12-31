from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List, Dict


# ---------- BASIC INFO ----------

class BasicInfoSchema(BaseModel):
    full_name: str
    email: EmailStr
    role: Optional[str] = None
    bio: Optional[str] = None


# ---------- SOCIAL PROFILES ----------

class SocialProfilesSchema(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    website: Optional[str] = None
    others: Optional[Dict[str, str]] = None


# ---------- INFLUENTIAL CONTENT ----------

class InfluentialItemSchema(BaseModel):
    type: str
    title: str
    why: str


class InfluentialContentSchema(BaseModel):
    personal: List[InfluentialItemSchema] = []
    professional: List[InfluentialItemSchema] = []
    curiosity: List[InfluentialItemSchema] = []
    legacy: List[InfluentialItemSchema] = []


# ---------- VISION ----------

class VisionAnswerInputSchema(BaseModel):
    vision_question_id: UUID
    answer: str


# ---------- FINAL PAYLOAD ----------

class OnboardingSubmitSchema(BaseModel):
    basic_info: BasicInfoSchema
    social_profiles: SocialProfilesSchema
    influential_content: InfluentialContentSchema
    vision_answers: List[VisionAnswerInputSchema]

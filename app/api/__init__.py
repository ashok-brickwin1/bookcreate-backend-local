from fastapi import APIRouter


#from .v1 import organization, questionnaire
from app.api import (auth,book, chapter,
                      research,vision,
                      influence,onboarding,
                      book_user,answers,
                      life_moment,
                      common
                      )

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(research.router, prefix="/source-sites", tags=["Source Sites"])
api_router.include_router(vision.router, prefix="/vision", tags=["Vision"])
api_router.include_router(influence.router, prefix="/influence", tags=["Influence"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
api_router.include_router(book_user.router, prefix="/book-user", tags=["Book User"])
api_router.include_router(book.router, prefix="/book", tags=["Book"])
api_router.include_router(answers.router, prefix="/answers", tags=["Answers"])
api_router.include_router(life_moment.router, prefix="/life-moments", tags=["Life Moments"])
api_router.include_router(common.router, prefix="/common", tags=["Common"])



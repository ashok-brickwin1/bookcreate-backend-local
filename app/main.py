#main.py

from fastapi import FastAPI
from app.db.database import engine
from app.models import *  # imports all models
from app.core.config import settings
from app.db import database
# import models so metadata includes them
from app.models import user  # ensure your models package imports user
from app.api import auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import api_router

import logging
from logging.handlers import RotatingFileHandler

# root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler("app.log", maxBytes=5*1024*1024, backupCount=3)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


app = FastAPI(title="backend")

# 🔓 CORS (React → FastAPI)

origins = [
    "http://localhost:5173",  # React dev server (Vite default)
    "http://127.0.0.1:5173",
    "http://localhost:8080"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"msg": "Questionnaire Backend is running"}

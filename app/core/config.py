import os
from dotenv import load_dotenv

# Load .env from repository backend folder if present
_env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(_env_path)


# Simple config values read from environment or sensible defaults
project_name = os.getenv("PROJECT_NAME", "Book Backend")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bookcreate_db.db")
import logging

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # You can use DEBUG, WARNING, ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create a logger for your app
logger = logging.getLogger("fastapi_app")

# app/core/config.py
from pydantic_settings import BaseSettings
from datetime import timedelta

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    PROJECT_NAME: str = "Ec Writer"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    PERPLEXITY_API_KEY:str=os.getenv("PERPLEXITY_API_KEY", "")
    XAI_API_KEY:str=os.getenv("XAI_API_KEY", "")
    ENRICH_SO_API_KEY:str=os.getenv("ENRICH_SO_API_KEY", "")
    OPENAI_API_KEY:str=os.getenv("OPENAI_API_KEY", "")
    ALGORITHM: str = "HS256"
    API_V1_STR: str = "/api"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 28800  # 20 days   ( change here)

    class Config:
        env_file = ".env"

settings = Settings()

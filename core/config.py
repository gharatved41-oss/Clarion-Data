"""Core configuration module for merged Automated Insight Analyst Platform."""
import os
from pathlib import Path
from pydantic import BaseModel

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
STATIC_DIR = BASE_DIR / "static"

# Ensure runtime directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    """Application settings."""
    app_name: str = "Automated Insight Analyst API"
    app_version: str = "6.0.0"
    api_prefix: str = ""
    cors_origins: list[str] = ["*"]
    uploads_dir: Path = UPLOADS_DIR
    processed_dir: Path = PROCESSED_DIR
    static_dir: Path = STATIC_DIR


settings = Settings()

"""
애플리케이션 설정 관리
환경 변수를 로드하고 설정을 관리합니다.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """애플리케이션 설정 클래스"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:6245@localhost:5432/livestockmanagementsystem")
    
    # Application
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Project Info
    PROJECT_NAME: str = "Livestock Management System"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "축산 관리 시스템 - 소 개체 관리 및 번식 일정 추적"
    
    # CORS (필요시 추가)
    ALLOWED_ORIGINS: list = ["http://localhost:8000", "http://127.0.0.1:8000"]


# 설정 인스턴스 생성
settings = Settings()
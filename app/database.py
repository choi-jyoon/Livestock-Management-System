"""
데이터베이스 연결 설정
SQLAlchemy 엔진, 세션, Base 클래스 설정
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# SQLAlchemy 엔진 생성
# pool_pre_ping: 연결 상태를 체크하여 끊어진 연결을 자동으로 재연결
# echo: SQL 쿼리 로깅 (개발 중에는 True, 프로덕션에서는 False)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG  # DEBUG 모드일 때만 쿼리 로깅
)

# 세션 로컬 생성
# autocommit=False: 명시적으로 commit 해야 함
# autoflush=False: 명시적으로 flush 해야 함
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base 클래스 생성 (모든 모델이 상속받을 클래스)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 의존성
    FastAPI의 Depends에서 사용
    
    Yields:
        Session: SQLAlchemy 데이터베이스 세션
    
    Example:
        @app.get("/cattle")
        def get_cattle(db: Session = Depends(get_db)):
            return db.query(Cattle).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    데이터베이스 초기화
    모든 테이블 생성 (개발 중에만 사용, 프로덕션에서는 Alembic 사용)
    """
    # 모든 모델을 import 해야 Base.metadata.create_all()이 제대로 작동함
    # 나중에 models를 만들면 여기서 import
    # from app.models import cattle, breeding, note, event, statistics
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def drop_db():
    """
    데이터베이스 모든 테이블 삭제 (주의: 개발 중에만 사용!)
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All database tables dropped!")
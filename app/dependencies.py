"""
FastAPI 의존성 주입 (Dependency Injection)
데이터베이스 세션, 페이지네이션 등 공통 의존성 정의
"""
from typing import Generator, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, Query, HTTPException, status

from app.database import SessionLocal


# ============================================
# 데이터베이스 세션 의존성
# ============================================

def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 의존성
    요청마다 새로운 세션 생성 및 자동 종료
    
    Usage:
        @app.get("/cattle")
        def get_cattle(db: Session = Depends(get_db)):
            return db.query(Cattle).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# 페이지네이션 의존성
# ============================================

class Pagination:
    """페이지네이션 파라미터"""
    
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="건너뛸 개수"),
        limit: int = Query(100, ge=1, le=1000, description="가져올 개수")
    ):
        self.skip = skip
        self.limit = limit


def get_pagination(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
) -> dict:
    """
    페이지네이션 파라미터 계산
    
    Args:
        page: 페이지 번호 (1부터 시작)
        page_size: 페이지당 항목 수
    
    Returns:
        dict: skip, limit 값
    """
    skip = (page - 1) * page_size
    return {"skip": skip, "limit": page_size}


# ============================================
# 필터링 의존성
# ============================================

class CattleFilter:
    """소 필터링 파라미터"""
    
    def __init__(
        self,
        gender: Optional[str] = Query(None, description="성별 필터 (male/female/freemartin)"),
        status: Optional[str] = Query(None, description="상태 필터 (active/sold/deceased)"),
        search: Optional[str] = Query(None, description="개체번호 검색")
    ):
        self.gender = gender
        self.status = status
        self.search = search


class EventFilter:
    """이벤트 필터링 파라미터"""
    
    def __init__(
        self,
        event_type: Optional[str] = Query(None, description="이벤트 타입"),
        is_completed: Optional[bool] = Query(None, description="완료 여부"),
        date_from: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
        date_to: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)")
    ):
        self.event_type = event_type
        self.is_completed = is_completed
        self.date_from = date_from
        self.date_to = date_to


# ============================================
# 엔티티 존재 확인 의존성
# ============================================

async def get_cattle_or_404(
    cattle_id: int,
    db: Session = Depends(get_db)
):
    """
    소 ID로 조회, 없으면 404 에러
    
    Usage:
        @app.get("/cattle/{cattle_id}")
        def get_cattle_detail(cattle: Cattle = Depends(get_cattle_or_404)):
            return cattle
    """
    from app.models import Cattle
    
    cattle = db.query(Cattle).filter(Cattle.id == cattle_id).first()
    if not cattle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cattle with id {cattle_id} not found"
        )
    return cattle


async def get_breeding_record_or_404(
    breeding_id: int,
    db: Session = Depends(get_db)
):
    """수정 기록 ID로 조회, 없으면 404 에러"""
    from app.models import BreedingRecord
    
    record = db.query(BreedingRecord).filter(BreedingRecord.id == breeding_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Breeding record with id {breeding_id} not found"
        )
    return record


async def get_event_or_404(
    event_id: int,
    db: Session = Depends(get_db)
):
    """이벤트 로그 ID로 조회, 없으면 404 에러"""
    from app.models import EventLog
    
    event = db.query(EventLog).filter(EventLog.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    return event
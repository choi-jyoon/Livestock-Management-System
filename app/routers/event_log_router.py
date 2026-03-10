"""
Event API Router
이벤트 관련 API 엔드포인트 (5가지 이벤트 타입)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.event_log_service import EventService

router = APIRouter()


@router.get("/summary")
def get_all_events_summary(db: Session = Depends(get_db)):
    """
    모든 이벤트 요약 (대시보드용)
    
    5가지 이벤트 타입:
    1. breeding_due - 수정 예정
    2. estrus_check - 재발정 확인 (수정 후 20일) 🆕
    3. pregnancy_check - 임신 확인 (수정 후 30-60일)
    4. birth_due - 출산 예정 (수정일 + 285일) 🆕
    5. birth_overdue - 출산 지연 🆕
    """
    service = EventService(db)
    return service.get_all_events_summary()


@router.get("/counts")
def get_event_counts(db: Session = Depends(get_db)):
    """
    이벤트 개수 요약
    
    각 이벤트 타입별 개수 반환
    """
    service = EventService(db)
    return service.get_event_counts()


@router.get("/breeding-due")
def get_breeding_due(db: Session = Depends(get_db)):
    """
    수정 예정 소 조회
    
    조건:
    - 송아지: 출생 후 12개월 경과 & 수정 이력 없음
    - 어미소: 출산 후 30-45일 사이
    """
    service = EventService(db)
    return service.calculate_breeding_due()


@router.get("/estrus-check")
def get_estrus_check(db: Session = Depends(get_db)):
    """
    재발정 확인 대상 조회 🆕
    
    조건:
    - 수정일로부터 18-22일 경과
    - 결과가 아직 pending 상태
    
    중요: 발정이 오지 않으면 임신 가능성 높음!
    """
    service = EventService(db)
    return service.calculate_estrus_check()


@router.get("/pregnancy-check")
def get_pregnancy_check(db: Session = Depends(get_db)):
    """
    임신 확인 대상 조회
    
    조건:
    - 수정일로부터 30-60일 경과
    - 결과가 아직 pending 상태
    """
    service = EventService(db)
    return service.calculate_pregnancy_check()


@router.get("/birth-due")
def get_birth_due(db: Session = Depends(get_db)):
    """
    출산 예정 소 조회 🆕
    
    조건:
    - 수정 결과가 pregnant
    - 출산 예정일 = 수정일 + 285일
    - 예정일 기준 ±7일 이내
    """
    service = EventService(db)
    return service.calculate_birth_due()


@router.get("/birth-overdue")
def get_birth_overdue(db: Session = Depends(get_db)):
    """
    출산 지연 소 조회 🆕
    
    조건:
    - 출산 예정일을 초과했지만 아직 출산 안 함
    
    긴급도:
    - 3일 이상: 긴급 확인 필요
    - 5일 이상: 수의사 연락 필수
    - 7일 이상: 즉시 수의사 검진
    """
    service = EventService(db)
    return service.calculate_birth_overdue()


@router.get("/today")
def get_today_events(db: Session = Depends(get_db)):
    """
    오늘의 이벤트
    
    오늘 발생하는 모든 이벤트 조회
    """
    service = EventService(db)
    all_events = service.get_all_events_summary()
    
    # 오늘 날짜 기준으로 필터링 (간단한 버전)
    return {
        "breeding_due": all_events["breeding_due"][:5],  # 상위 5개
        "estrus_check": all_events["estrus_check"],
        "pregnancy_check": all_events["pregnancy_check"][:5],
        "birth_due": all_events["birth_due"],
        "birth_overdue": all_events["birth_overdue"]
    }
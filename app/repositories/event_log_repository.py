"""
Event Repository
이벤트 로그 관련 데이터베이스 접근 계층
"""
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.models.event_log import EventLog, EventTypeEnum
from app.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository[EventLog]):
    """이벤트 로그(EventLog) Repository"""
    
    def __init__(self, db: Session):
        super().__init__(EventLog, db)
    
    # ============================================
    # 기본 조회
    # ============================================
    
    def get_by_cattle_id(self, cattle_id: int) -> List[EventLog]:
        """특정 소의 이벤트 로그"""
        return self.db.query(EventLog).filter(
            EventLog.cattle_id == cattle_id
        ).order_by(EventLog.event_date.desc()).all()
    
    def get_by_type(self, event_type: EventTypeEnum) -> List[EventLog]:
        """특정 타입의 이벤트 로그"""
        return self.db.query(EventLog).filter(
            EventLog.event_type == event_type,
            EventLog.is_completed == False
        ).order_by(EventLog.event_date).all()
    
    def get_by_date(self, target_date: date) -> List[EventLog]:
        """특정 날짜의 이벤트 로그"""
        return self.db.query(EventLog).filter(
            EventLog.event_date == target_date,
            EventLog.is_completed == False
        ).all()
    
    def get_pending_events(self) -> List[EventLog]:
        """완료되지 않은 모든 이벤트"""
        return self.db.query(EventLog).filter(
            EventLog.is_completed == False
        ).order_by(EventLog.event_date).all()
    
    # ============================================
    # 완료 처리
    # ============================================
    
    def mark_as_completed(self, id: int) -> Optional[EventLog]:
        """이벤트 완료 처리"""
        event = self.get(id)
        if not event:
            return None
        
        event.is_completed = True
        event.completed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(event)
        return event
"""
EventLog 관련 Pydantic 스키마
이벤트 로그 API 요청/응답 데이터 검증
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum


# Enum 정의 (5가지 이벤트 타입)
class EventTypeEnum(str, Enum):
    BREEDING_DUE = "breeding_due"  # 수정 예정
    ESTRUS_CHECK = "estrus_check"  # 재발정 확인 (수정 후 20일)
    PREGNANCY_CHECK = "pregnancy_check"  # 임신 확인 (수정 후 30-60일)
    BIRTH_DUE = "birth_due"  # 출산 예정
    BIRTH_OVERDUE = "birth_overdue"  # 출산 지연


# Base 스키마
class EventLogBase(BaseModel):
    cattle_id: int = Field(..., description="소 ID")
    event_date: date = Field(..., description="이벤트 날짜")
    event_type: EventTypeEnum = Field(..., description="이벤트 타입")
    description: Optional[str] = Field(None, max_length=500, description="설명")


# 생성 스키마
class EventLogCreate(EventLogBase):
    """이벤트 로그 생성"""
    pass


# 수정 스키마
class EventLogUpdate(BaseModel):
    """이벤트 로그 수정"""
    event_date: Optional[date] = None
    event_type: Optional[EventTypeEnum] = None
    description: Optional[str] = Field(None, max_length=500)
    is_completed: Optional[bool] = None


# 완료 처리 스키마
class EventLogComplete(BaseModel):
    """이벤트 완료 처리"""
    is_completed: bool = Field(True, description="완료 여부")


# 응답 스키마
class EventLogResponse(EventLogBase):
    """이벤트 로그 응답"""
    id: int
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 리스트 응답
class EventLogListResponse(BaseModel):
    """이벤트 로그 리스트"""
    total: int
    items: list[EventLogResponse]


# 대시보드용 이벤트 요약
class EventSummary(BaseModel):
    """대시보드용 이벤트 요약"""
    breeding_due: list[EventLogResponse] = Field(default_factory=list, description="수정 예정")
    estrus_check: list[EventLogResponse] = Field(default_factory=list, description="재발정 확인")
    pregnancy_check: list[EventLogResponse] = Field(default_factory=list, description="임신 확인")
    birth_due: list[EventLogResponse] = Field(default_factory=list, description="출산 예정")
    birth_overdue: list[EventLogResponse] = Field(default_factory=list, description="출산 지연")
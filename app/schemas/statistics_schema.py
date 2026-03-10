"""
Statistics 관련 Pydantic 스키마
통계 API 응답 데이터 검증
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime


# Base 스키마
class StatisticsBase(BaseModel):
    stat_date: date = Field(..., description="통계 날짜")
    total_cattle: int = Field(default=0, ge=0, description="전체 소 마리 수")
    pregnant_count: int = Field(default=0, ge=0, description="임신 중인 소")
    bred_count: int = Field(default=0, ge=0, description="수정한 소 (결과 대기)")
    breeding_due_count: int = Field(default=0, ge=0, description="수정 예정 소")
    birth_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="출산율 (%)")
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="수정 성공률 (%)")


# 생성/수정 스키마
class StatisticsCreate(StatisticsBase):
    """통계 생성"""
    pass


class StatisticsUpdate(StatisticsBase):
    """통계 수정"""
    pass


# 응답 스키마
class StatisticsResponse(StatisticsBase):
    """통계 응답"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 대시보드 요약 통계
class DashboardSummary(BaseModel):
    """대시보드 요약 통계"""
    pregnant_count: int = Field(..., description="임신 중인 소")
    bred_count: int = Field(..., description="수정한 소 (결과 대기)")
    breeding_due_count: int = Field(..., description="수정 예정 소")
    success_rate: float = Field(..., description="수정 성공률 (%)")
    
    # 이벤트 카운트
    estrus_check_count: int = Field(default=0, description="재발정 확인 대상")
    pregnancy_check_count: int = Field(default=0, description="임신 확인 대상")
    birth_due_count: int = Field(default=0, description="출산 예정 소")
    birth_overdue_count: int = Field(default=0, description="출산 지연 소")


# 월별 통계 (차트용)
class MonthlyStatistics(BaseModel):
    """월별 통계"""
    month: str = Field(..., description="월 (YYYY-MM)")
    birth_count: int = Field(default=0, description="출산 수")
    breeding_count: int = Field(default=0, description="수정 수")
    success_count: int = Field(default=0, description="임신 성공 수")
    success_rate: float = Field(default=0.0, description="성공률 (%)")
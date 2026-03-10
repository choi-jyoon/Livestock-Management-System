"""
BreedingRecord 관련 Pydantic 스키마
수정 기록 API 요청/응답 데이터 검증
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum


# Enum 정의
class BreedingResultEnum(str, Enum):
    PENDING = "PENDING"
    PREGNANT = "PREGNANT"
    FAILED = "FAILED"


class BirthTypeEnum(str, Enum):
    EASY = "EASY"
    DIFFICULT = "DIFFICULT"


# Base 스키마
class BreedingRecordBase(BaseModel):
    cattle_id: int = Field(..., description="소 ID")
    breeding_date: date = Field(..., description="수정일")
    semen_id: Optional[str] = Field(None, max_length=50, description="정액 번호")
    notes: Optional[str] = Field(None, max_length=500, description="메모")


# 생성 스키마
class BreedingRecordCreate(BreedingRecordBase):
    """수정 기록 생성"""
    pass


# 수정 스키마
class BreedingRecordUpdate(BaseModel):
    """수정 기록 업데이트 (모든 필드 Optional)"""
    breeding_date: Optional[date] = None
    semen_id: Optional[str] = Field(None, max_length=50)
    result: Optional[BreedingResultEnum] = None
    result_check_date: Optional[date] = None
    expected_calving_date: Optional[date] = None
    actual_calving_date: Optional[date] = None
    birth_type: Optional[BirthTypeEnum] = None
    notes: Optional[str] = Field(None, max_length=500)


# 결과 업데이트 전용 스키마
class BreedingResultUpdate(BaseModel):
    """수정 결과만 업데이트 (임신/실패)"""
    result: BreedingResultEnum = Field(..., description="수정 결과")
    result_check_date: date = Field(..., description="결과 확인일")


# 출산 정보 업데이트 전용 스키마
class BirthInfoUpdate(BaseModel):
    """출산 정보 업데이트"""
    actual_calving_date: date = Field(..., description="실제 출산일")
    birth_type: BirthTypeEnum = Field(..., description="출산 유형 (순산/난산)")


# 응답 스키마
class BreedingRecordResponse(BreedingRecordBase):
    """수정 기록 응답"""
    id: int
    result: BreedingResultEnum
    result_check_date: Optional[date]
    expected_calving_date: Optional[date]
    actual_calving_date: Optional[date]
    birth_type: Optional[BirthTypeEnum]
    pregnancy_months: int = Field(..., description="임신 경과 개월 수")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 리스트 응답
class BreedingRecordListResponse(BaseModel):
    """수정 기록 리스트"""
    total: int
    items: list[BreedingRecordResponse]
"""
Cattle 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum


# Enum 정의
class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    FREEMARTIN = "FREEMARTIN"


class StatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    DECEASED = "DECEASED"


# Base 스키마 (공통 필드)
class CattleBase(BaseModel):
    identification_number: str = Field(..., min_length=1, max_length=50, description="개체 식별 번호")
    gender: GenderEnum = Field(..., description="성별")
    birth_date: date = Field(..., description="출생일")
    status: StatusEnum = Field(default=StatusEnum.ACTIVE, description="상태")
    mother_id: Optional[int] = Field(None, description="모 개체 ID")


# 생성 스키마 (POST 요청)
class CattleCreate(CattleBase):
    """소 생성 시 필요한 데이터"""
    pass


# 수정 스키마 (PUT/PATCH 요청)
class CattleUpdate(BaseModel):
    """소 수정 시 필요한 데이터 (모든 필드 Optional)"""
    identification_number: Optional[str] = Field(None, min_length=1, max_length=50)
    gender: Optional[GenderEnum] = None
    birth_date: Optional[date] = None
    status: Optional[StatusEnum] = None
    mother_id: Optional[int] = None


# 응답 스키마 (GET 응답)
class CattleResponse(CattleBase):
    """API 응답용 소 데이터"""
    id: int
    age_months: int = Field(..., description="개월 수 (자동 계산)")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)  # ORM 모델과 호환


# 리스트 응답 스키마
class CattleListResponse(BaseModel):
    """소 리스트 응답"""
    total: int
    items: list[CattleResponse]
"""
CattleNote 관련 Pydantic 스키마
특이사항 기록 API 요청/응답 데이터 검증
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum


# Enum 정의
class NoteTypeEnum(str, Enum):
    SYMPTOM = "SYMPTOM"
    TREATMENT = "TREATMENT"
    BIRTH = "BIRTH"
    OTHER = "OTHER"


# Base 스키마
class CattleNoteBase(BaseModel):
    cattle_id: int = Field(..., description="소 ID")
    note_date: date = Field(..., description="기록 날짜")
    note_type: NoteTypeEnum = Field(..., description="기록 유형")
    content: str = Field(..., min_length=1, max_length=2000, description="내용")


# 생성 스키마
class CattleNoteCreate(CattleNoteBase):
    """특이사항 생성"""
    pass


# 수정 스키마
class CattleNoteUpdate(BaseModel):
    """특이사항 수정 (모든 필드 Optional)"""
    note_date: Optional[date] = None
    note_type: Optional[NoteTypeEnum] = None
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    is_active: Optional[bool] = None


# 응답 스키마
class CattleNoteResponse(CattleNoteBase):
    """특이사항 응답"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 리스트 응답
class CattleNoteListResponse(BaseModel):
    """특이사항 리스트"""
    total: int
    items: list[CattleNoteResponse]
"""
Note API Router
특이사항 관련 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.cattle_note_service import CattleNoteService
from app.schemas.cattle_note_schema  import (
    CattleNoteCreate,
    CattleNoteUpdate,
    CattleNoteResponse
)

router = APIRouter()


@router.post("/", response_model=CattleNoteResponse, status_code=201)
def create_note(
    note_data: CattleNoteCreate,
    db: Session = Depends(get_db)
):
    """
    특이사항 생성
    
    - **note_type**: symptom (증상), treatment (투약), birth (출산), other (기타)
    """
    service = CattleNoteService(db)
    return service.create_note(note_data)


@router.get("/cattle/{cattle_id}", response_model=List[CattleNoteResponse])
def get_notes_by_cattle(
    cattle_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """특정 소의 특이사항 조회"""
    service = CattleNoteService(db)
    return service.get_notes_by_cattle(cattle_id, skip, limit)


@router.put("/{note_id}", response_model=CattleNoteResponse)
def update_note(
    note_id: int,
    note_data: CattleNoteUpdate,
    db: Session = Depends(get_db)
):
    """특이사항 수정"""
    service = CattleNoteService(db)
    return service.update_note(note_id, note_data)


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    """특이사항 삭제"""
    service = CattleNoteService(db)
    service.delete_note(note_id)
    return {"message": "Note deleted successfully"}
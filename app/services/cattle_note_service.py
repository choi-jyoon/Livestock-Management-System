"""
Note Service
특이사항 관련 비즈니스 로직
"""
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.cattle_note import CattleNote
from app.repositories.cattle_note_repository import NoteRepository
from app.repositories.cattle_repository import CattleRepository
from app.schemas.cattle_note_schema import CattleNoteCreate, CattleNoteUpdate


class CattleNoteService:
    """특이사항 비즈니스 로직"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = NoteRepository(db)
        self.cattle_repo = CattleRepository(db)
    
    def create_note(self, note_data: CattleNoteCreate) -> CattleNote:
        """특이사항 생성"""
        # 소 존재 확인
        cattle = self.cattle_repo.get(note_data.cattle_id)
        if not cattle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cattle with id {note_data.cattle_id} not found"
            )
        
        note_dict = note_data.model_dump()
        return self.repository.create(note_dict)
    
    def get_notes_by_cattle(
        self,
        cattle_id: int,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[CattleNote]:
        """특정 소의 특이사항 리스트 (active_only=False → 전체, True → 활성만)"""
        return self.repository.get_by_cattle_id(cattle_id, skip, limit, active_only=active_only)
    
    def update_note(self, note_id: int, note_data: CattleNoteUpdate) -> CattleNote:
        """특이사항 수정"""
        note = self.repository.get(note_id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note with id {note_id} not found"
            )
        
        update_dict = note_data.model_dump(exclude_unset=True)
        updated = self.repository.update(note_id, update_dict)
        
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update note"
            )
        
        return updated
    
    def delete_note(self, note_id: int) -> bool:
        """특이사항 삭제"""
        return self.repository.delete(note_id)
"""
Note Repository
소 특이사항 관련 데이터베이스 접근 계층
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from app.models.cattle_note import CattleNote, NoteTypeEnum
from app.repositories.base_repository import BaseRepository


class NoteRepository(BaseRepository[CattleNote]):
    """특이사항(CattleNote) Repository"""
    
    def __init__(self, db: Session):
        super().__init__(CattleNote, db)
    
    # ============================================
    # 기본 조회
    # ============================================
    
    def get_by_cattle_id(
        self,
        cattle_id: int,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[CattleNote]:
        """
        특정 소의 특이사항 조회

        Args:
            cattle_id: 소 ID
            skip: 건너뛸 개수
            limit: 가져올 개수
            active_only: True이면 활성(is_active=True)인 것만 조회

        Returns:
            CattleNote 리스트 (최신순)
        """
        q = self.db.query(CattleNote).filter(CattleNote.cattle_id == cattle_id)
        if active_only:
            q = q.filter(CattleNote.is_active == True)
        return q.order_by(CattleNote.note_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_date_range(
        self,
        cattle_id: int,
        start_date: date,
        end_date: date
    ) -> List[CattleNote]:
        """
        특정 기간의 특이사항 조회
        
        Args:
            cattle_id: 소 ID
            start_date: 시작 날짜
            end_date: 종료 날짜
        
        Returns:
            CattleNote 리스트
        """
        return self.db.query(CattleNote).filter(
            CattleNote.cattle_id == cattle_id,
            CattleNote.note_date >= start_date,
            CattleNote.note_date <= end_date
        ).order_by(CattleNote.note_date.desc()).all()
    
    # ============================================
    # 타입별 조회
    # ============================================
    
    def get_by_type(
        self,
        cattle_id: int,
        note_type: NoteTypeEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[CattleNote]:
        """
        특정 유형의 특이사항 조회
        
        Args:
            cattle_id: 소 ID
            note_type: 특이사항 유형 (symptom/treatment/birth/other)
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            CattleNote 리스트
        """
        return self.db.query(CattleNote).filter(
            CattleNote.cattle_id == cattle_id,
            CattleNote.note_type == note_type
        ).order_by(CattleNote.note_date.desc()).offset(skip).limit(limit).all()
    
    def get_symptoms(self, cattle_id: int) -> List[CattleNote]:
        """증상 기록만 조회"""
        return self.get_by_type(cattle_id, NoteTypeEnum.SYMPTOM)
    
    def get_treatments(self, cattle_id: int) -> List[CattleNote]:
        """투약/치료 기록만 조회"""
        return self.get_by_type(cattle_id, NoteTypeEnum.TREATMENT)
    
    def get_births(self, cattle_id: int) -> List[CattleNote]:
        """출산 기록만 조회"""
        return self.get_by_type(cattle_id, NoteTypeEnum.BIRTH)
    
    # ============================================
    # 검색
    # ============================================
    
    def search_content(
        self,
        cattle_id: int,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CattleNote]:
        """
        내용으로 검색
        
        Args:
            cattle_id: 소 ID
            keyword: 검색 키워드
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            검색 결과 CattleNote 리스트
        """
        return self.db.query(CattleNote).filter(
            CattleNote.cattle_id == cattle_id,
            CattleNote.content.ilike(f"%{keyword}%")
        ).order_by(CattleNote.note_date.desc()).offset(skip).limit(limit).all()
    
    # ============================================
    # 통계용
    # ============================================
    
    def count_by_cattle_id(self, cattle_id: int) -> int:
        """특정 소의 특이사항 개수"""
        return self.db.query(CattleNote).filter(
            CattleNote.cattle_id == cattle_id
        ).count()
    
    def count_by_type(self, cattle_id: int, note_type: NoteTypeEnum) -> int:
        """특정 유형의 특이사항 개수"""
        return self.db.query(CattleNote).filter(
            CattleNote.cattle_id == cattle_id,
            CattleNote.note_type == note_type
        ).count()
    
    # ============================================
    # 최근 기록
    # ============================================
    
    def get_recent_notes(self, cattle_id: int, limit: int = 5, active_only: bool = True) -> List[CattleNote]:
        """
        최근 특이사항 조회

        Args:
            cattle_id: 소 ID
            limit: 가져올 개수
            active_only: True이면 활성(is_active=True)인 것만 조회 (기본값: True)

        Returns:
            최근 CattleNote 리스트
        """
        q = self.db.query(CattleNote).filter(CattleNote.cattle_id == cattle_id)
        if active_only:
            q = q.filter(CattleNote.is_active == True)
        return q.order_by(CattleNote.note_date.desc()).limit(limit).all()
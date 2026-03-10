"""
Cattle Repository
소 관련 데이터베이스 접근 계층
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.cattle import Cattle, GenderEnum, StatusEnum
from app.repositories.base_repository import BaseRepository


class CattleRepository(BaseRepository[Cattle]):
    """소(Cattle) Repository"""
    
    def __init__(self, db: Session):
        super().__init__(Cattle, db)
    
    # ============================================
    # 특화된 조회 메서드
    # ============================================
    
    def get_by_identification_number(self, identification_number: str) -> Optional[Cattle]:
        """
        개체 식별 번호로 조회
        
        Args:
            identification_number: 개체 식별 번호
        
        Returns:
            Cattle 인스턴스 또는 None
        """
        return self.db.query(Cattle).filter(
            Cattle.identification_number == identification_number
        ).first()
    
    def get_by_gender(self, gender: GenderEnum, skip: int = 0, limit: int = 100) -> List[Cattle]:
        """
        성별로 조회
        
        Args:
            gender: 성별 (male/female/freemartin)
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            Cattle 리스트
        """
        return self.db.query(Cattle).filter(
            Cattle.gender == gender
        ).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: StatusEnum, skip: int = 0, limit: int = 100) -> List[Cattle]:
        """
        상태로 조회
        
        Args:
            status: 상태 (active/sold/deceased)
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            Cattle 리스트
        """
        return self.db.query(Cattle).filter(
            Cattle.status == status
        ).offset(skip).limit(limit).all()
    
    def get_active_cattle(self, skip: int = 0, limit: int = 100) -> List[Cattle]:
        """
        활성 상태의 소만 조회
        
        Args:
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            활성 상태 Cattle 리스트
        """
        return self.get_by_status(StatusEnum.ACTIVE, skip, limit)
    
    def get_female_cattle(self, skip: int = 0, limit: int = 100) -> List[Cattle]:
        """
        암소만 조회 (번식 가능)
        
        Args:
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            암소 리스트
        """
        return self.get_by_gender(GenderEnum.FEMALE, skip, limit)
    
    def get_children(self, mother_id: int) -> List[Cattle]:
        """
        특정 모의 자식들 조회
        
        Args:
            mother_id: 모 개체 ID
        
        Returns:
            자식 Cattle 리스트
        """
        return self.db.query(Cattle).filter(
            Cattle.mother_id == mother_id
        ).all()
    
    def search_by_identification(self, keyword: str, skip: int = 0, limit: int = 100) -> List[Cattle]:
        """
        개체 식별 번호로 검색 (부분 일치)
        
        Args:
            keyword: 검색 키워드
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            검색 결과 Cattle 리스트
        """
        return self.db.query(Cattle).filter(
            Cattle.identification_number.ilike(f"%{keyword}%")
        ).offset(skip).limit(limit).all()
    
    def get_cattle_with_filters(
        self,
        gender: Optional[GenderEnum] = None,
        status: Optional[StatusEnum] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cattle]:
        """
        복합 필터로 소 조회
        
        Args:
            gender: 성별 필터
            status: 상태 필터
            search: 검색 키워드 (개체번호)
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            필터링된 Cattle 리스트
        """
        query = self.db.query(Cattle)
        
        if gender:
            query = query.filter(Cattle.gender == gender)
        
        if status:
            query = query.filter(Cattle.status == status)
        
        if search:
            query = query.filter(Cattle.identification_number.ilike(f"%{search}%"))
        
        return query.offset(skip).limit(limit).all()
    
    def count_with_filters(
        self,
        gender: Optional[GenderEnum] = None,
        status: Optional[StatusEnum] = None,
        search: Optional[str] = None
    ) -> int:
        """
        필터링된 소 개수
        
        Args:
            gender: 성별 필터
            status: 상태 필터
            search: 검색 키워드
        
        Returns:
            개수
        """
        query = self.db.query(Cattle)
        
        if gender:
            query = query.filter(Cattle.gender == gender)
        
        if status:
            query = query.filter(Cattle.status == status)
        
        if search:
            query = query.filter(Cattle.identification_number.ilike(f"%{search}%"))
        
        return query.count()
    
    # ============================================
    # 통계용 메서드
    # ============================================
    
    def count_by_gender(self, gender: GenderEnum) -> int:
        """성별로 개수 세기"""
        return self.db.query(Cattle).filter(Cattle.gender == gender).count()
    
    def count_by_status(self, status: StatusEnum) -> int:
        """상태로 개수 세기"""
        return self.db.query(Cattle).filter(Cattle.status == status).count()
    
    def get_total_active_count(self) -> int:
        """활성 상태 소 전체 개수"""
        return self.count_by_status(StatusEnum.ACTIVE)
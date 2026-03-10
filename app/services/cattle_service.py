"""
Cattle Service
소 관련 비즈니스 로직
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.cattle import Cattle, GenderEnum, StatusEnum
from app.repositories.cattle_repository import CattleRepository
from app.schemas.cattle_schema import CattleCreate, CattleUpdate


class CattleService:
    """소(Cattle) 비즈니스 로직"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CattleRepository(db)
    
    # ============================================
    # CRUD
    # ============================================
    
    def create_cattle(self, cattle_data: CattleCreate) -> Cattle:
        """
        새 소 등록
        
        Args:
            cattle_data: 소 생성 데이터
        
        Returns:
            생성된 Cattle
        
        Raises:
            HTTPException: 개체번호 중복 시
        """
        # 개체번호 중복 확인
        existing = self.repository.get_by_identification_number(
            cattle_data.identification_number
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cattle with identification number '{cattle_data.identification_number}' already exists"
            )
        
        # 모 개체 존재 확인
        if cattle_data.mother_id:
            mother = self.repository.get(cattle_data.mother_id)
            if not mother:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Mother cattle with id {cattle_data.mother_id} not found"
                )
            
            # 모는 암소여야 함
            if mother.gender != GenderEnum.FEMALE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mother must be female"
                )
        
        # 생성
        cattle_dict = cattle_data.model_dump()
        return self.repository.create(cattle_dict)
    
    def get_cattle_by_id(self, cattle_id: int) -> Optional[Cattle]:
        """ID로 소 조회"""
        cattle = self.repository.get(cattle_id)
        if not cattle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cattle with id {cattle_id} not found"
            )
        return cattle
    
    def get_all_cattle(
        self,
        skip: int = 0,
        limit: int = 100,
        gender: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, any]:
        """
        소 리스트 조회 (필터링, 페이지네이션)
        
        Returns:
            dict: {"total": int, "items": List[Cattle]}
        """
        # Enum 변환
        gender_enum = GenderEnum(gender) if gender else None
        status_enum = StatusEnum(status) if status else None
        
        # 조회
        cattle_list = self.repository.get_cattle_with_filters(
            gender=gender_enum,
            status=status_enum,
            search=search,
            skip=skip,
            limit=limit
        )
        
        total = self.repository.count_with_filters(
            gender=gender_enum,
            status=status_enum,
            search=search
        )
        
        return {
            "total": total,
            "items": cattle_list
        }
    
    def update_cattle(self, cattle_id: int, cattle_data: CattleUpdate) -> Cattle:
        """
        소 정보 수정
        
        Args:
            cattle_id: 소 ID
            cattle_data: 수정할 데이터
        
        Returns:
            수정된 Cattle
        """
        # 존재 확인
        cattle = self.get_cattle_by_id(cattle_id)
        
        # 개체번호 중복 확인 (변경하는 경우)
        if cattle_data.identification_number:
            existing = self.repository.get_by_identification_number(
                cattle_data.identification_number
            )
            if existing and existing.id != cattle_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cattle with identification number '{cattle_data.identification_number}' already exists"
                )
        
        # 수정
        update_dict = cattle_data.model_dump(exclude_unset=True)
        updated = self.repository.update(cattle_id, update_dict)
        
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update cattle"
            )
        
        return updated
    
    def delete_cattle(self, cattle_id: int) -> bool:
        """
        소 삭제 (상태를 deceased로 변경)
        실제 삭제 대신 상태 변경 권장
        """
        cattle = self.get_cattle_by_id(cattle_id)
        
        # 상태를 deceased로 변경
        cattle.status = StatusEnum.DECEASED
        self.db.commit()
        
        return True
    
    # ============================================
    # 특화 메서드
    # ============================================
    
    def get_female_cattle_for_breeding(self) -> List[Cattle]:
        """번식 가능한 암소 리스트 (활성 상태의 암소)"""
        return self.db.query(Cattle).filter(
            Cattle.gender == GenderEnum.FEMALE,
            Cattle.status == StatusEnum.ACTIVE
        ).all()
    
    def get_children(self, mother_id: int) -> List[Cattle]:
        """특정 모의 자식들"""
        return self.repository.get_children(mother_id)
    
    def get_cattle_statistics(self) -> Dict[str, int]:
        """소 통계"""
        return {
            "total_active": self.repository.get_total_active_count(),
            "total_male": self.repository.count_by_gender(GenderEnum.MALE),
            "total_female": self.repository.count_by_gender(GenderEnum.FEMALE),
            "total_freemartin": self.repository.count_by_gender(GenderEnum.FREEMARTIN),
            "total_sold": self.repository.count_by_status(StatusEnum.SOLD),
            "total_deceased": self.repository.count_by_status(StatusEnum.DECEASED),
        }
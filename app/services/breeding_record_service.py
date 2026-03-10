"""
Breeding Service
수정 기록 관련 비즈니스 로직
"""
from typing import List, Optional, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.breeding_record import BreedingRecord, BreedingResultEnum, BirthTypeEnum
from app.repositories.breeding_record_repository import BreedingRecordRepository
from app.repositories.cattle_repository import CattleRepository
from app.schemas.breeding_record_schema import (
    BreedingRecordCreate,
    BreedingRecordUpdate,
    BreedingResultUpdate,
    BirthInfoUpdate
)


class BreedingService:
    """수정 기록 비즈니스 로직"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = BreedingRecordRepository(db)
        self.cattle_repo = CattleRepository(db)
    
    # ============================================
    # CRUD
    # ============================================
    
    def create_breeding_record(self, breeding_data: BreedingRecordCreate) -> BreedingRecord:
        """
        새 수정 기록 생성
        
        Args:
            breeding_data: 수정 기록 생성 데이터
        
        Returns:
            생성된 BreedingRecord
        """
        # 소 존재 확인
        cattle = self.cattle_repo.get(breeding_data.cattle_id)
        if not cattle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cattle with id {breeding_data.cattle_id} not found"
            )
        
        # 암소만 수정 가능
        from app.models.cattle import GenderEnum
        if cattle.gender != GenderEnum.FEMALE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only female cattle can be bred"
            )
        
        # 수정 기록 생성
        breeding_dict = breeding_data.model_dump()
        record = self.repository.create(breeding_dict)
        
        # 출산 예정일 자동 계산 (수정일 + 285일)
        record.calculate_expected_calving_date()
        self.db.commit()
        self.db.refresh(record)
        
        return record
    
    def get_breeding_record_by_id(self, breeding_id: int) -> BreedingRecord:
        """ID로 수정 기록 조회"""
        record = self.repository.get(breeding_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Breeding record with id {breeding_id} not found"
            )
        return record
    
    def get_breeding_records_by_cattle(self, cattle_id: int) -> List[BreedingRecord]:
        """특정 소의 모든 수정 기록"""
        # 소 존재 확인
        cattle = self.cattle_repo.get(cattle_id)
        if not cattle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cattle with id {cattle_id} not found"
            )
        
        return self.repository.get_by_cattle_id(cattle_id)
    
    def update_breeding_record(
        self,
        breeding_id: int,
        breeding_data: BreedingRecordUpdate
    ) -> BreedingRecord:
        """수정 기록 업데이트"""
        # 존재 확인
        record = self.get_breeding_record_by_id(breeding_id)
        
        # 업데이트
        update_dict = breeding_data.model_dump(exclude_unset=True)
        
        # 수정일이 변경되면 출산 예정일 재계산
        if "breeding_date" in update_dict:
            record.breeding_date = update_dict["breeding_date"]
            record.calculate_expected_calving_date()
        
        updated = self.repository.update(breeding_id, update_dict)
        
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update breeding record"
            )
        
        return updated
    
    def delete_breeding_record(self, breeding_id: int) -> bool:
        """수정 기록 삭제"""
        record = self.get_breeding_record_by_id(breeding_id)
        return self.repository.delete(breeding_id)
    
    # ============================================
    # 결과 업데이트
    # ============================================
    
    def update_breeding_result(
        self,
        breeding_id: int,
        result_data: BreedingResultUpdate
    ) -> BreedingRecord:
        """
        수정 결과 업데이트 (임신/실패)
        
        Args:
            breeding_id: 수정 기록 ID
            result_data: 결과 데이터
        
        Returns:
            업데이트된 BreedingRecord
        """
        record = self.repository.update_result(
            breeding_id,
            result_data.result,
            result_data.result_check_date
        )
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Breeding record with id {breeding_id} not found"
            )
        
        return record
    
    def update_birth_info(
        self,
        breeding_id: int,
        birth_data: BirthInfoUpdate
    ) -> BreedingRecord:
        """
        출산 정보 업데이트
        
        Args:
            breeding_id: 수정 기록 ID
            birth_data: 출산 정보
        
        Returns:
            업데이트된 BreedingRecord
        """
        record = self.repository.update_birth_info(
            breeding_id,
            birth_data.actual_calving_date,
            birth_data.birth_type
        )
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Breeding record with id {breeding_id} not found"
            )
        
        return record
    
    # ============================================
    # 통계
    # ============================================
    
    def get_breeding_statistics(self) -> Dict[str, any]:
        """수정 통계"""
        return {
            "total_pregnant": self.repository.count_pregnant(),
            "total_pending": self.repository.count_bred_pending(),
            "total_failed": self.repository.count_by_result(BreedingResultEnum.FAILED),
            "success_rate_6months": round(self.repository.calculate_success_rate(180), 1),
            "success_rate_12months": round(self.repository.calculate_success_rate(365), 1),
        }
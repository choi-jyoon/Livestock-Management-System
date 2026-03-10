"""
Breeding Repository
수정 기록 관련 데이터베이스 접근 계층
"""
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.breeding_record import BreedingRecord, BreedingResultEnum, BirthTypeEnum
from app.repositories.base_repository import BaseRepository


class BreedingRecordRepository(BaseRepository[BreedingRecord]):
    """수정 기록(BreedingRecord) Repository"""
    
    def __init__(self, db: Session):
        super().__init__(BreedingRecord, db)
    
    # ============================================
    # 기본 조회
    # ============================================
    
    def get_by_cattle_id(self, cattle_id: int) -> List[BreedingRecord]:
        """
        특정 소의 모든 수정 기록 조회
        
        Args:
            cattle_id: 소 ID
        
        Returns:
            BreedingRecord 리스트 (최신순)
        """
        return self.db.query(BreedingRecord).filter(
            BreedingRecord.cattle_id == cattle_id
        ).order_by(BreedingRecord.breeding_date.desc()).all()
    
    def get_latest_by_cattle_id(self, cattle_id: int) -> Optional[BreedingRecord]:
        """
        특정 소의 가장 최근 수정 기록
        
        Args:
            cattle_id: 소 ID
        
        Returns:
            가장 최근 BreedingRecord 또는 None
        """
        return self.db.query(BreedingRecord).filter(
            BreedingRecord.cattle_id == cattle_id
        ).order_by(BreedingRecord.breeding_date.desc()).first()
    
    # ============================================
    # 결과별 조회
    # ============================================
    
    def get_by_result(
        self,
        result: BreedingResultEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[BreedingRecord]:
        """
        수정 결과로 조회
        
        Args:
            result: 수정 결과 (pending/pregnant/failed)
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            BreedingRecord 리스트
        """
        return self.db.query(BreedingRecord).filter(
            BreedingRecord.result == result
        ).offset(skip).limit(limit).all()
    
    def get_pending_records(self, skip: int = 0, limit: int = 100) -> List[BreedingRecord]:
        """결과 대기 중인 수정 기록"""
        return self.get_by_result(BreedingResultEnum.PENDING, skip, limit)
    
    def get_pregnant_records(self, skip: int = 0, limit: int = 100) -> List[BreedingRecord]:
        """임신 확인된 수정 기록"""
        return self.get_by_result(BreedingResultEnum.PREGNANT, skip, limit)
    
    def get_failed_records(self, skip: int = 0, limit: int = 100) -> List[BreedingRecord]:
        """임신 실패한 수정 기록"""
        return self.get_by_result(BreedingResultEnum.FAILED, skip, limit)
    
    # ============================================
    # 이벤트 계산용 조회 (5가지 타입)
    # ============================================
    
    def get_for_estrus_check(self, target_date: Optional[date] = None) -> List[BreedingRecord]:
        """
        재발정 확인 대상 (수정 후 18-22일)
        
        Args:
            target_date: 기준 날짜 (기본: 오늘)
        
        Returns:
            재발정 확인 대상 BreedingRecord 리스트
        """
        if not target_date:
            target_date = date.today()
        
        # 수정일이 18-22일 전인 기록
        start_date = target_date - timedelta(days=22)
        end_date = target_date - timedelta(days=18)
        
        return self.db.query(BreedingRecord).filter(
            and_(
                BreedingRecord.result == BreedingResultEnum.PENDING,
                BreedingRecord.breeding_date >= start_date,
                BreedingRecord.breeding_date <= end_date
            )
        ).all()
    
    def get_for_pregnancy_check(self, target_date: Optional[date] = None) -> List[BreedingRecord]:
        """
        임신 확인 대상 (수정 후 30-60일)
        
        Args:
            target_date: 기준 날짜 (기본: 오늘)
        
        Returns:
            임신 확인 대상 BreedingRecord 리스트
        """
        if not target_date:
            target_date = date.today()
        
        # 수정일이 30-60일 전인 기록
        start_date = target_date - timedelta(days=60)
        end_date = target_date - timedelta(days=30)
        
        return self.db.query(BreedingRecord).filter(
            and_(
                BreedingRecord.result == BreedingResultEnum.PENDING,
                BreedingRecord.breeding_date >= start_date,
                BreedingRecord.breeding_date <= end_date
            )
        ).all()
    
    def get_for_birth_due(
        self,
        days_range: int = 7,
        target_date: Optional[date] = None
    ) -> List[BreedingRecord]:
        """
        출산 예정 대상 (예정일 기준 ±days_range일)
        
        Args:
            days_range: 예정일로부터 며칠 범위
            target_date: 기준 날짜 (기본: 오늘)
        
        Returns:
            출산 예정 BreedingRecord 리스트
        """
        if not target_date:
            target_date = date.today()
        
        start_date = target_date - timedelta(days=days_range)
        end_date = target_date + timedelta(days=days_range)
        
        return self.db.query(BreedingRecord).filter(
            and_(
                BreedingRecord.result == BreedingResultEnum.PREGNANT,
                BreedingRecord.actual_calving_date.is_(None),  # 아직 출산 안 함
                BreedingRecord.expected_calving_date >= start_date,
                BreedingRecord.expected_calving_date <= end_date
            )
        ).order_by(BreedingRecord.expected_calving_date).all()
    
    def get_for_birth_overdue(self, target_date: Optional[date] = None) -> List[BreedingRecord]:
        """
        출산 지연 대상 (예정일 초과)
        
        Args:
            target_date: 기준 날짜 (기본: 오늘)
        
        Returns:
            출산 지연 BreedingRecord 리스트
        """
        if not target_date:
            target_date = date.today()
        
        return self.db.query(BreedingRecord).filter(
            and_(
                BreedingRecord.result == BreedingResultEnum.PREGNANT,
                BreedingRecord.actual_calving_date.is_(None),  # 아직 출산 안 함
                BreedingRecord.expected_calving_date < target_date  # 예정일 초과
            )
        ).order_by(BreedingRecord.expected_calving_date).all()
    
    # ============================================
    # 통계용 조회
    # ============================================
    
    def count_by_result(self, result: BreedingResultEnum) -> int:
        """수정 결과별 개수"""
        return self.db.query(BreedingRecord).filter(
            BreedingRecord.result == result
        ).count()
    
    def count_pregnant(self) -> int:
        """임신 중인 소 개수"""
        return self.db.query(BreedingRecord).filter(
            and_(
                BreedingRecord.result == BreedingResultEnum.PREGNANT,
                BreedingRecord.actual_calving_date.is_(None)
            )
        ).count()
    
    def count_bred_pending(self) -> int:
        """수정 후 결과 대기 중인 소 개수"""
        return self.count_by_result(BreedingResultEnum.PENDING)
    
    def calculate_success_rate(self, days: int = 180) -> float:
        """
        수정 성공률 계산 (최근 N일)
        
        Args:
            days: 기간 (일)
        
        Returns:
            성공률 (%)
        """
        cutoff_date = date.today() - timedelta(days=days)
        
        # 결과가 확인된 기록 (임신 or 실패)
        total = self.db.query(BreedingRecord).filter(
            and_(
                BreedingRecord.result_check_date >= cutoff_date,
                BreedingRecord.result.in_([BreedingResultEnum.PREGNANT, BreedingResultEnum.FAILED])
            )
        ).count()
        
        # 임신 성공
        success = self.db.query(BreedingRecord).filter(
            and_(
                BreedingRecord.result_check_date >= cutoff_date,
                BreedingRecord.result == BreedingResultEnum.PREGNANT
            )
        ).count()
        
        return (success / total * 100) if total > 0 else 0.0
    
    # ============================================
    # 업데이트 헬퍼
    # ============================================
    
    def update_result(
        self,
        id: int,
        result: BreedingResultEnum,
        result_check_date: date
    ) -> Optional[BreedingRecord]:
        """
        수정 결과 업데이트
        
        Args:
            id: 수정 기록 ID
            result: 결과 (pregnant/failed)
            result_check_date: 결과 확인일
        
        Returns:
            업데이트된 BreedingRecord
        """
        record = self.get(id)
        if not record:
            return None
        
        record.result = result
        record.result_check_date = result_check_date
        
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def update_birth_info(
        self,
        id: int,
        actual_calving_date: date,
        birth_type: BirthTypeEnum
    ) -> Optional[BreedingRecord]:
        """
        출산 정보 업데이트
        
        Args:
            id: 수정 기록 ID
            actual_calving_date: 실제 출산일
            birth_type: 출산 유형 (easy/difficult)
        
        Returns:
            업데이트된 BreedingRecord
        """
        record = self.get(id)
        if not record:
            return None
        
        record.actual_calving_date = actual_calving_date
        record.birth_type = birth_type
        
        self.db.commit()
        self.db.refresh(record)
        return record
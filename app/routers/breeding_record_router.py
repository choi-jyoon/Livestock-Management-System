"""
Breeding API Router
수정 기록 관련 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.breeding_record_service import BreedingService
from app.schemas.breeding_record_schema import (
    BreedingRecordCreate,
    BreedingRecordUpdate,
    BreedingResultUpdate,
    BirthInfoUpdate,
    BreedingRecordResponse,
    BreedingRecordListResponse
)

router = APIRouter()


@router.post("/", response_model=BreedingRecordResponse, status_code=201)
def create_breeding_record(
    breeding_data: BreedingRecordCreate,
    db: Session = Depends(get_db)
):
    """
    새 수정 기록 생성
    
    - 출산 예정일은 자동 계산 (수정일 + 285일)
    """
    service = BreedingService(db)
    return service.create_breeding_record(breeding_data)


@router.get("/cattle/{cattle_id}", response_model=List[BreedingRecordResponse])
def get_breeding_records_by_cattle(
    cattle_id: int,
    db: Session = Depends(get_db)
):
    """특정 소의 모든 수정 기록 조회"""
    service = BreedingService(db)
    return service.get_breeding_records_by_cattle(cattle_id)


@router.get("/{breeding_id}", response_model=BreedingRecordResponse)
def get_breeding_record(
    breeding_id: int,
    db: Session = Depends(get_db)
):
    """수정 기록 단일 조회"""
    service = BreedingService(db)
    return service.get_breeding_record_by_id(breeding_id)


@router.put("/{breeding_id}", response_model=BreedingRecordResponse)
def update_breeding_record(
    breeding_id: int,
    breeding_data: BreedingRecordUpdate,
    db: Session = Depends(get_db)
):
    """수정 기록 업데이트"""
    service = BreedingService(db)
    return service.update_breeding_record(breeding_id, breeding_data)


@router.put("/{breeding_id}/result", response_model=BreedingRecordResponse)
def update_breeding_result(
    breeding_id: int,
    result_data: BreedingResultUpdate,
    db: Session = Depends(get_db)
):
    """
    수정 결과 업데이트
    
    - result: pregnant (임신) / failed (실패)
    - result_check_date: 결과 확인일
    """
    service = BreedingService(db)
    return service.update_breeding_result(breeding_id, result_data)


@router.put("/{breeding_id}/birth", response_model=BreedingRecordResponse)
def update_birth_info(
    breeding_id: int,
    birth_data: BirthInfoUpdate,
    db: Session = Depends(get_db)
):
    """
    출산 정보 업데이트
    
    - actual_calving_date: 실제 출산일
    - birth_type: easy (순산) / difficult (난산)
    """
    service = BreedingService(db)
    return service.update_birth_info(breeding_id, birth_data)


@router.delete("/{breeding_id}")
def delete_breeding_record(
    breeding_id: int,
    db: Session = Depends(get_db)
):
    """수정 기록 삭제"""
    service = BreedingService(db)
    service.delete_breeding_record(breeding_id)
    return {"message": "Breeding record deleted successfully"}


@router.get("/statistics/summary")
def get_breeding_statistics(db: Session = Depends(get_db)):
    """수정 통계"""
    service = BreedingService(db)
    return service.get_breeding_statistics()
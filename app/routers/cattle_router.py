"""
Cattle API Router
소 관련 API 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.cattle_service import CattleService
from app.schemas.cattle_schema import (
    CattleCreate,
    CattleUpdate,
    CattleResponse,
    CattleListResponse
)

router = APIRouter()


@router.post("/", response_model=CattleResponse, status_code=201)
def create_cattle(
    cattle_data: CattleCreate,
    db: Session = Depends(get_db)
):
    """
    새 소 등록
    
    - **identification_number**: 개체 식별 번호 (고유값)
    - **gender**: 성별 (male/female/freemartin)
    - **birth_date**: 출생일
    - **mother_id**: 모 개체 ID (선택)
    """
    service = CattleService(db)
    return service.create_cattle(cattle_data)


@router.get("/", response_model=CattleListResponse)
def get_all_cattle(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="가져올 개수"),
    gender: Optional[str] = Query(None, description="성별 필터"),
    status: Optional[str] = Query(None, description="상태 필터"),
    search: Optional[str] = Query(None, description="개체번호 검색"),
    db: Session = Depends(get_db)
):
    """
    소 리스트 조회
    
    필터링:
    - **gender**: male, female, freemartin
    - **status**: active, sold, deceased
    - **search**: 개체번호 부분 검색
    
    페이지네이션:
    - **skip**: 건너뛸 개수
    - **limit**: 가져올 개수
    """
    service = CattleService(db)
    return service.get_all_cattle(skip, limit, gender, status, search)


@router.get("/{cattle_id}", response_model=CattleResponse)
def get_cattle_by_id(
    cattle_id: int,
    db: Session = Depends(get_db)
):
    """ID로 소 조회"""
    service = CattleService(db)
    return service.get_cattle_by_id(cattle_id)


@router.put("/{cattle_id}", response_model=CattleResponse)
def update_cattle(
    cattle_id: int,
    cattle_data: CattleUpdate,
    db: Session = Depends(get_db)
):
    """소 정보 수정"""
    service = CattleService(db)
    return service.update_cattle(cattle_id, cattle_data)


@router.delete("/{cattle_id}")
def delete_cattle(
    cattle_id: int,
    db: Session = Depends(get_db)
):
    """소 삭제 (상태를 deceased로 변경)"""
    service = CattleService(db)
    service.delete_cattle(cattle_id)
    return {"message": "Cattle deleted successfully"}


@router.get("/{cattle_id}/children", response_model=List[CattleResponse])
def get_children(
    cattle_id: int,
    db: Session = Depends(get_db)
):
    """특정 모의 자식들 조회"""
    service = CattleService(db)
    return service.get_children(cattle_id)


@router.get("/statistics/summary")
def get_cattle_statistics(db: Session = Depends(get_db)):
    """소 통계"""
    service = CattleService(db)
    return service.get_cattle_statistics()
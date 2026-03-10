
"""
Cattle Page Routers
소 리스트 & 상세 페이지
"""
from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db
from app.services.cattle_service import CattleService
from app.services.breeding_record_service import BreedingService
from app.services.cattle_note_service import CattleNoteService
from app.services.event_log_service import EventService
from app.repositories.breeding_record_repository import BreedingRecordRepository
from app.repositories.cattle_note_repository import NoteRepository
from app.models.breeding_record import BreedingResultEnum

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/cattle")
async def cattle_list(
    request: Request,
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    filter: Optional[str] = Query(None)
    # pregnant | bred | breeding_due | estrus_check | pregnancy_check | birth_due | birth_overdue
):
    """소 리스트 페이지"""
    cattle_service = CattleService(db)
    breeding_repo = BreedingRecordRepository(db)

    # 이벤트 필터 → 라벨 매핑
    EVENT_FILTER_LABELS = {
        "pregnant":       "임신 중인 소",
        "bred":           "수정한 소 (결과 대기)",
        "breeding_due":   "수정 예정",
        "estrus_check":   "재발정 확인",
        "pregnancy_check":"임신 확인",
        "birth_due":      "출산 예정",
        "birth_overdue":  "출산 지연 (긴급)",
    }

    # 대시보드 카드에서 넘어온 특수 필터 처리
    page_filter_label = None
    if filter == "pregnant":
        records = breeding_repo.get_pregnant_records(limit=10000)
        cattle_ids = list({r.cattle_id for r in records})
        cattle_list_items = [cattle_service.repository.get(cid) for cid in cattle_ids]
        cattle_list_items = [c for c in cattle_list_items if c]
        total = len(cattle_list_items)
        page_filter_label = EVENT_FILTER_LABELS["pregnant"]

    elif filter == "bred":
        records = breeding_repo.get_pending_records(limit=10000)
        cattle_ids = list({r.cattle_id for r in records})
        cattle_list_items = [cattle_service.repository.get(cid) for cid in cattle_ids]
        cattle_list_items = [c for c in cattle_list_items if c]
        total = len(cattle_list_items)
        page_filter_label = EVENT_FILTER_LABELS["bred"]

    elif filter in ("breeding_due", "estrus_check", "pregnancy_check", "birth_due", "birth_overdue"):
        # 이벤트 서비스에서 해당 이벤트의 cattle_id 목록 추출
        event_service = EventService(db)
        event_map = {
            "breeding_due":    event_service.calculate_breeding_due,
            "estrus_check":    event_service.calculate_estrus_check,
            "pregnancy_check": event_service.calculate_pregnancy_check,
            "birth_due":       event_service.calculate_birth_due,
            "birth_overdue":   event_service.calculate_birth_overdue,
        }
        events = event_map[filter]()
        # 중복 제거 후 cattle 객체 조회 (이벤트 순서 유지)
        seen = set()
        cattle_ids_ordered = []
        for ev in events:
            cid = ev["cattle_id"]
            if cid not in seen:
                seen.add(cid)
                cattle_ids_ordered.append(cid)
        cattle_list_items = [cattle_service.repository.get(cid) for cid in cattle_ids_ordered]
        cattle_list_items = [c for c in cattle_list_items if c]
        total = len(cattle_list_items)
        page_filter_label = EVENT_FILTER_LABELS[filter]

    else:
        result = cattle_service.get_all_cattle(
            skip=0,
            limit=100,
            gender=gender,
            status=status,
            search=search
        )
        cattle_list_items = result["items"]
        total = result["total"]

    # 소별 최근 특이사항 유형 목록 수집 (리스트에서 이모지 표시용)
    # { cattle_id: set of NoteTypeEnum values }
    note_repo = NoteRepository(db)
    notes_type_map: dict = {}
    for c in cattle_list_items:
        recent = note_repo.get_recent_notes(c.id, limit=5)
        if recent:
            notes_type_map[c.id] = {n.note_type.value for n in recent}

    # 모 개체 identification_number 매핑 { mother_id: identification_number }
    mother_ids = {c.mother_id for c in cattle_list_items if c.mother_id}
    mother_number_map: dict = {}
    for mid in mother_ids:
        m = cattle_service.repository.get(mid)
        if m:
            num = m.identification_number
            mother_number_map[mid] = num[9:13] if len(num) >= 13 else num

    return templates.TemplateResponse("cattle_list.html", {
        "request": request,
        "cattle_list": cattle_list_items,
        "total": total,
        "page_filter_label": page_filter_label,
        "current_filter": filter,
        "notes_type_map": notes_type_map,
        "mother_number_map": mother_number_map,
    })


@router.get("/cattle/new")
async def cattle_new(
    request: Request,
    db: Session = Depends(get_db)
):
    """새 소 등록 페이지"""
    cattle_service = CattleService(db)
    all_cattle = cattle_service.get_all_cattle(skip=0, limit=1000)

    return templates.TemplateResponse("cattle_new.html", {
        "request": request,
        "all_cattle": all_cattle["items"]
    })


@router.get("/cattle/{cattle_id}")
async def cattle_detail(
    request: Request,
    cattle_id: int,
    db: Session = Depends(get_db)
):
    """소 상세 페이지"""
    cattle_service = CattleService(db)
    breeding_service = BreedingService(db)
    note_service = CattleNoteService(db)

    cattle = cattle_service.get_cattle_by_id(cattle_id)
    breeding_records = breeding_service.get_breeding_records_by_cattle(cattle_id)
    notes = note_service.get_notes_by_cattle(cattle_id, limit=10)

    # 모 개체 조회 (있으면 identification_number 표시용)
    mother = None
    if cattle.mother_id:
        try:
            mother = cattle_service.get_cattle_by_id(cattle.mother_id)
        except Exception:
            mother = None

    # 자식 개체 목록 (backref "children" 활용)
    children = sorted(cattle.children, key=lambda c: c.birth_date or "", reverse=True)

    # 모 개체 선택용 전체 암소 목록 (자기 자신 제외)
    all_cattle_result = cattle_service.get_all_cattle(skip=0, limit=1000, gender="FEMALE")
    all_female_cattle = [c for c in all_cattle_result["items"] if c.id != cattle_id]

    return templates.TemplateResponse("cattle_detail.html", {
        "request": request,
        "cattle": cattle,
        "breeding_records": breeding_records,
        "notes": notes,
        "mother": mother,
        "children": children,
        "all_female_cattle": all_female_cattle,
    })

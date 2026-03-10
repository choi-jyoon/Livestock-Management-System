
"""
Dashboard Page Router
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.event_log_service import EventService
from app.services.breeding_record_service import BreedingService
from app.repositories.cattle_repository import CattleRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    event_service = EventService(db)
    breeding_service = BreedingService(db)
    cattle_repo = CattleRepository(db)
    
    stats = {
        "pregnant_count": breeding_service.repository.count_pregnant(),
        "bred_count": breeding_service.repository.count_bred_pending(),
        "total_cattle": cattle_repo.get_total_active_count(),
        "success_rate": breeding_service.repository.calculate_success_rate(180)
    }
    
    events = event_service.get_all_events_summary()
    event_counts = event_service.get_event_counts()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "events": events,
        "event_counts": event_counts
    })
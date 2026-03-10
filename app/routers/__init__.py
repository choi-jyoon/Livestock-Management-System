"""
모든 Router를 한 곳에서 import
"""
from app.routers import cattle_router, breeding_record_router, event_log_router, cattle_note_router

__all__ = [
    "cattle_router",
    "breeding_record_router",
    "event_log_router",
    "cattle_note_router",
]
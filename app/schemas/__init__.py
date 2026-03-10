"""
모든 Pydantic 스키마를 한 곳에서 import
"""
from app.schemas.cattle_schema import (
    CattleBase,
    CattleCreate,
    CattleUpdate,
    CattleResponse,
    CattleListResponse,
    GenderEnum as CattleGenderEnum,
    StatusEnum as CattleStatusEnum,
)

from app.schemas.breeding_record_schema import (
    BreedingRecordBase,
    BreedingRecordCreate,
    BreedingRecordUpdate,
    BreedingResultUpdate,
    BirthInfoUpdate,
    BreedingRecordResponse,
    BreedingRecordListResponse,
    BreedingResultEnum,
    BirthTypeEnum,
)

from app.schemas.cattle_note_schema import (
    CattleNoteBase,
    CattleNoteCreate,
    CattleNoteUpdate,
    CattleNoteResponse,
    CattleNoteListResponse,
    NoteTypeEnum,
)

from app.schemas.event_log_schema import (
    EventLogBase,
    EventLogCreate,
    EventLogUpdate,
    EventLogComplete,
    EventLogResponse,
    EventLogListResponse,
    EventSummary,
    EventTypeEnum,
)

from app.schemas.statistics_schema import (
    StatisticsBase,
    StatisticsCreate,
    StatisticsUpdate,
    StatisticsResponse,
    DashboardSummary,
    MonthlyStatistics,
)

__all__ = [
    # Cattle
    "CattleBase",
    "CattleCreate",
    "CattleUpdate",
    "CattleResponse",
    "CattleListResponse",
    "CattleGenderEnum",
    "CattleStatusEnum",
    
    # Breeding
    "BreedingRecordBase",
    "BreedingRecordCreate",
    "BreedingRecordUpdate",
    "BreedingResultUpdate",
    "BirthInfoUpdate",
    "BreedingRecordResponse",
    "BreedingRecordListResponse",
    "BreedingResultEnum",
    "BirthTypeEnum",
    
    # Note
    "CattleNoteBase",
    "CattleNoteCreate",
    "CattleNoteUpdate",
    "CattleNoteResponse",
    "CattleNoteListResponse",
    "NoteTypeEnum",
    
    # Event
    "EventLogBase",
    "EventLogCreate",
    "EventLogUpdate",
    "EventLogComplete",
    "EventLogResponse",
    "EventLogListResponse",
    "EventSummary",
    "EventTypeEnum",
    
    # Statistics
    "StatisticsBase",
    "StatisticsCreate",
    "StatisticsUpdate",
    "StatisticsResponse",
    "DashboardSummary",
    "MonthlyStatistics",
]
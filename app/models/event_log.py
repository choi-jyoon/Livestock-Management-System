from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from .mixins import TimestampMixin
import enum

class EventTypeEnum(str, enum.Enum):
    BREEDING_DUE = "BREEDING_DUE"  # 수정 예정
    ESTRUS_CHECK = "ESTRUS_CHECK"  # 재발정 확인 (수정 후 20일)
    PREGNANCY_CHECK = "PREGNANCY_CHECK"  # 임신 확인 (수정 후 30-60일)
    BIRTH_DUE = "BIRTH_DUE"  # 출산 예정
    BIRTH_OVERDUE = "BIRTH_OVERDUE"  # 출산 지연

class EventLog(Base, TimestampMixin):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    cattle_id = Column(Integer, ForeignKey("cattle.id"), nullable=False)
    event_date = Column(Date, nullable=False)
    event_type = Column(SQLEnum(EventTypeEnum), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)  # 완료 일시
    is_active = Column(Integer, default=1)  # 1: active, 0: inactive (soft delete)
    

    cattle = relationship("Cattle", back_populates="event_logs")

    def __repr__(self):
        return f"<EventLog(id={self.id}, cattle_id={self.cattle_id}, type={self.event_type.value}, completed={self.is_completed})>"
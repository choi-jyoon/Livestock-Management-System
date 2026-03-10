from sqlalchemy import Column, Integer, String, Date, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from .mixins import TimestampMixin
from datetime import datetime, date
import enum

# Enum 정의
class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    FREEMARTIN = "FREEMARTIN"

class StatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    DECEASED = "DECEASED"

class Cattle(Base, TimestampMixin):
    __tablename__ = "cattle"

    id = Column(Integer, primary_key=True, index=True)
    identification_number = Column(String, unique=True, index=True, nullable=False)
    gender = Column(SQLEnum(GenderEnum), nullable=False)
    birth_date = Column(Date, nullable=False)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    is_active = Column(Integer, default=1)  # 1: active, 0: inactive (soft delete)
    
    # 모 개체 (자기참조)
    mother_id = Column(Integer, ForeignKey("cattle.id"), nullable=True)
    
    # 관계 설정
    mother = relationship("Cattle", remote_side=[id], backref="children")
    breeding_records = relationship("BreedingRecord", back_populates="cattle", cascade="all, delete-orphan")
    event_logs = relationship("EventLog", back_populates="cattle", cascade="all, delete-orphan")
    notes = relationship("CattleNote", back_populates="cattle", cascade="all, delete-orphan")
    father_kpn = Column(String, nullable=True)

    @property
    def age_months(self) -> int:
        """출생일로부터 개월 수 자동 계산"""
        if not self.birth_date:
            return 0
        today = date.today()
        months = (today.year - self.birth_date.year) * 12 + (today.month - self.birth_date.month)
        return max(0, months)

    def __repr__(self):
        return f"<Cattle(id={self.id}, number='{self.identification_number}', gender='{self.gender.value}')>"
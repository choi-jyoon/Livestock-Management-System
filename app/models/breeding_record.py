from app.database import Base 
from sqlalchemy import Column, Integer, String, Date, Enum as SQLEnum, ForeignKey 
from sqlalchemy.orm import relationship 
from .mixins import TimestampMixin
from datetime import date, timedelta
import enum

# Enum 정의
class BreedingResultEnum(str, enum.Enum):
    PENDING = "PENDING"  # 결과 대기
    PREGNANT = "PREGNANT"  # 임신 확인
    FAILED = "FAILED"  # 임신 실패

class BirthTypeEnum(str, enum.Enum):
    EASY = "EASY"  # 순산
    DIFFICULT = "DIFFICULT"  # 난산

class BreedingRecord(Base, TimestampMixin):
    __tablename__ = "breeding_records"

    id = Column(Integer, primary_key=True, index=True)
    cattle_id = Column(Integer, ForeignKey("cattle.id"), nullable=False)
    breeding_date = Column(Date, nullable=False)
    semen_id = Column(String, nullable=True)  # 정액 번호
    is_active = Column(Integer, default=1)  # 1: active, 0: inactive (soft delete)
    
    
    # 결과 관련
    result = Column(SQLEnum(BreedingResultEnum), default=BreedingResultEnum.PENDING, nullable=False)
    result_check_date = Column(Date, nullable=True)  # 결과 확인일

    # 출산 관련
    expected_calving_date = Column(Date, nullable=True)  # 출산 예정일 (수정일 + 285일)
    actual_calving_date = Column(Date, nullable=True)  # 실제 출산일
    birth_type = Column(SQLEnum(BirthTypeEnum), nullable=True)  # 난산/순산
    
    notes = Column(String, nullable=True)

    # 관계
    cattle = relationship("Cattle", back_populates="breeding_records")

    @property
    def pregnancy_months(self) -> int:
        """임신 경과 개월 수 계산"""
        if self.result != BreedingResultEnum.PREGNANT or not self.breeding_date:
            return 0
        
        # 출산했으면 0 반환
        if self.actual_calving_date:
            return 0
            
        today = date.today()
        months = (today.year - self.breeding_date.year) * 12 + (today.month - self.breeding_date.month)
        return max(0, months)
    
    def calculate_expected_calving_date(self):
        """출산 예정일 자동 계산 (수정일 + 285일)"""
        if self.breeding_date:
            self.expected_calving_date = self.breeding_date + timedelta(days=285)

    def __repr__(self):
        return f"<BreedingRecord(id={self.id}, cattle_id={self.cattle_id}, date={self.breeding_date}, result={self.result.value})>"
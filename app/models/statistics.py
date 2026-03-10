from sqlalchemy import Column, Integer, Date, Float
from app.database import Base
from .mixins import TimestampMixin

class Statistics(Base, TimestampMixin):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    stat_date = Column(Date, unique=True, nullable=False, index=True)
    
    # 통계 수치
    total_cattle = Column(Integer, default=0)
    pregnant_count = Column(Integer, default=0)
    bred_count = Column(Integer, default=0)  # 수정했으나 결과 대기
    breeding_due_count = Column(Integer, default=0)
    
    # 비율
    birth_rate = Column(Float, default=0.0)  # 출산율
    success_rate = Column(Float, default=0.0)  # 수정 성공률

    def __repr__(self):
        return f"<Statistics(date={self.stat_date}, total={self.total_cattle}, pregnant={self.pregnant_count})>"
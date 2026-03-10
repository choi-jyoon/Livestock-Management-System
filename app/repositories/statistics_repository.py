"""
Statistics Repository
통계 관련 데이터베이스 접근 계층
"""
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.models.statistics import Statistics
from app.repositories.base_repository import BaseRepository


class StatisticsRepository(BaseRepository[Statistics]):
    """통계(Statistics) Repository"""
    
    def __init__(self, db: Session):
        super().__init__(Statistics, db)
    
    def get_by_date(self, stat_date: date) -> Optional[Statistics]:
        """특정 날짜의 통계"""
        return self.db.query(Statistics).filter(
            Statistics.stat_date == stat_date
        ).first()
    
    def get_latest(self) -> Optional[Statistics]:
        """가장 최근 통계"""
        return self.db.query(Statistics).order_by(
            Statistics.stat_date.desc()
        ).first()
    
    def upsert(self, stat_date: date, data: dict) -> Statistics:
        """통계 업데이트 또는 생성"""
        stat = self.get_by_date(stat_date)
        
        if stat:
            # 업데이트
            for key, value in data.items():
                setattr(stat, key, value)
        else:
            # 생성
            stat = Statistics(stat_date=stat_date, **data)
            self.db.add(stat)
        
        self.db.commit()
        self.db.refresh(stat)
        return stat
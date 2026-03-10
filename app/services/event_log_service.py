"""
Event Service
이벤트 계산 및 관리 비즈니스 로직 (5가지 이벤트 타입)
"""
from typing import List, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.cattle import Cattle
from app.models.breeding_record import BreedingRecord, BreedingResultEnum
from app.repositories.cattle_repository import CattleRepository
from app.repositories.breeding_record_repository import BreedingRecordRepository


class EventService:
    """이벤트 계산 및 관리"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cattle_repo = CattleRepository(db)
        self.breeding_repo = BreedingRecordRepository(db)
    
    # ============================================
    # 1️⃣ 수정 예정 (Breeding Due)
    # ============================================
    
    def calculate_breeding_due(self) -> List[Dict]:
        """
        수정 예정 소 계산
        
        조건:
        - 송아지: 출생 후 12개월 경과 & 수정 이력 없음
        - 어미소: 출산 후 30-45일 사이
        
        Returns:
            수정 예정 소 리스트
        """
        today = date.today()
        breeding_due_list = []
        
        # 모든 활성 암소 조회
        from app.models.cattle import GenderEnum, StatusEnum
        female_cattle = self.db.query(Cattle).filter(
            Cattle.gender == GenderEnum.FEMALE,
            Cattle.status == StatusEnum.ACTIVE
        ).all()
        
        for cattle in female_cattle:
            # 수정 이력 조회
            breeding_records = self.breeding_repo.get_by_cattle_id(cattle.id)
            
            # 1) 송아지: 출생 후 12개월 경과 & 수정 이력 없음
            if cattle.age_months >= 12 and not breeding_records:
                breeding_due_list.append({
                    "cattle_id": cattle.id,
                    "cattle_number": cattle.identification_number,
                    "type": "calf_ready",
                    "message": f"수정 가능 (출생 {cattle.age_months}개월)",
                    "priority": "normal",
                    "days_info": cattle.age_months
                })
                continue
            
            # 2) 어미소: 마지막 출산 후 30-45일
            if breeding_records:
                # 가장 최근 출산 기록 찾기
                for record in breeding_records:
                    if record.actual_calving_date:
                        days_since_birth = (today - record.actual_calving_date).days
                        
                        if 30 <= days_since_birth <= 45:
                            breeding_due_list.append({
                                "cattle_id": cattle.id,
                                "cattle_number": cattle.identification_number,
                                "type": "mother_critical",
                                "message": f"출산 후 {days_since_birth}일 - 수정 필수 기간",
                                "priority": "high",
                                "days_info": days_since_birth,
                                "last_birth_date": record.actual_calving_date
                            })
                        elif days_since_birth > 45:
                            breeding_due_list.append({
                                "cattle_id": cattle.id,
                                "cattle_number": cattle.identification_number,
                                "type": "mother_overdue",
                                "message": f"출산 후 {days_since_birth}일 - 수정 지연!",
                                "priority": "urgent",
                                "days_info": days_since_birth,
                                "last_birth_date": record.actual_calving_date
                            })
                        break  # 가장 최근 출산만 확인
        
        return breeding_due_list
    
    # ============================================
    # 2️⃣ 재발정 확인 (Estrus Check) 🆕
    # ============================================
    
    def calculate_estrus_check(self) -> List[Dict]:
        """
        재발정 확인 대상 계산 (수정 후 20일)
        
        조건:
        - 수정일로부터 18-22일 경과
        - 결과가 아직 pending 상태
        
        Returns:
            재발정 확인 대상 리스트
        """
        today = date.today()
        estrus_check_list = []
        
        # 재발정 확인 대상 조회
        records = self.breeding_repo.get_for_estrus_check(today)
        
        for record in records:
            days_since = (today - record.breeding_date).days
            cattle = self.cattle_repo.get(record.cattle_id)
            
            if days_since == 20:
                priority = "high"
                message = "재발정 확인 D-Day! (수정 후 20일)"
            elif days_since < 20:
                priority = "normal"
                message = f"재발정 확인 예정 D-{20 - days_since}"
            else:
                priority = "normal"
                message = f"재발정 확인 기간 (수정 후 {days_since}일)"
            
            estrus_check_list.append({
                "cattle_id": record.cattle_id,
                "cattle_number": cattle.identification_number if cattle else "Unknown",
                "breeding_id": record.id,
                "breeding_date": record.breeding_date,
                "days_since": days_since,
                "check_date": record.breeding_date + timedelta(days=20),
                "message": message,
                "priority": priority,
                "note": "발정 없음 → 임신 가능성, 발정 있음 → 즉시 재수정"
            })
        
        return estrus_check_list
    
    # ============================================
    # 3️⃣ 임신 확인 (Pregnancy Check)
    # ============================================
    
    def calculate_pregnancy_check(self) -> List[Dict]:
        """
        임신 확인 대상 계산 (수정 후 30-60일)
        
        조건:
        - 수정일로부터 30-60일 경과
        - 결과가 아직 pending 상태
        
        Returns:
            임신 확인 대상 리스트
        """
        today = date.today()
        pregnancy_check_list = []
        
        # 임신 확인 대상 조회
        records = self.breeding_repo.get_for_pregnancy_check(today)
        
        for record in records:
            days_since = (today - record.breeding_date).days
            cattle = self.cattle_repo.get(record.cattle_id)
            
            if days_since >= 50:
                priority = "high"
                message = f"수정 후 {days_since}일 - 확인 필요"
            else:
                priority = "normal"
                message = f"수정 후 {days_since}일 - 확인 가능"
            
            pregnancy_check_list.append({
                "cattle_id": record.cattle_id,
                "cattle_number": cattle.identification_number if cattle else "Unknown",
                "breeding_id": record.id,
                "breeding_date": record.breeding_date,
                "days_since": days_since,
                "message": message,
                "priority": priority
            })
        
        return pregnancy_check_list
    
    # ============================================
    # 4️⃣ 출산 예정 (Birth Due) 🆕
    # ============================================
    
    def calculate_birth_due(self, days_range: int = 7) -> List[Dict]:
        """
        출산 예정 소 계산 (수정일 + 285일)
        
        조건:
        - 수정 결과가 pregnant
        - 출산 예정일 기준 ±days_range일 이내
        
        Args:
            days_range: 예정일로부터 며칠 범위
        
        Returns:
            출산 예정 소 리스트
        """
        today = date.today()
        birth_due_list = []
        
        # 출산 예정 대상 조회
        records = self.breeding_repo.get_for_birth_due(days_range, today)
        
        for record in records:
            cattle = self.cattle_repo.get(record.cattle_id)
            days_until_birth = (record.expected_calving_date - today).days
            
            if days_until_birth < 0:
                priority = "urgent"
                message = f"출산 예정일 {abs(days_until_birth)}일 경과! 🚨"
            elif days_until_birth == 0:
                priority = "critical"
                message = "오늘 출산 예정! 집중 관찰 필요 🚨🚨"
            elif days_until_birth <= 3:
                priority = "high"
                message = f"출산 예정 D-{days_until_birth}"
            else:
                priority = "normal"
                message = f"출산 예정 D-{days_until_birth}"
            
            birth_due_list.append({
                "cattle_id": record.cattle_id,
                "cattle_number": cattle.identification_number if cattle else "Unknown",
                "breeding_id": record.id,
                "breeding_date": record.breeding_date,
                "expected_date": record.expected_calving_date,
                "days_until": days_until_birth,
                "pregnancy_months": record.pregnancy_months,
                "message": message,
                "priority": priority
            })
        
        return birth_due_list
    
    # ============================================
    # 5️⃣ 출산 지연 (Birth Overdue) 🆕
    # ============================================
    
    def calculate_birth_overdue(self) -> List[Dict]:
        """
        출산 지연 알림 (예정일 초과)
        
        조건:
        - 출산 예정일을 초과했지만 아직 출산 안 함
        
        Returns:
            출산 지연 소 리스트
        """
        today = date.today()
        birth_overdue_list = []
        
        # 출산 지연 대상 조회
        records = self.breeding_repo.get_for_birth_overdue(today)
        
        for record in records:
            cattle = self.cattle_repo.get(record.cattle_id)
            days_overdue = (today - record.expected_calving_date).days
            
            if days_overdue >= 7:
                priority = "critical"
                message = f"출산 {days_overdue}일 지연! 즉시 수의사 연락 필수! 🚨🚨🚨"
                action = "긴급: 수의사 연락 및 즉시 검진"
            elif days_overdue >= 5:
                priority = "critical"
                message = f"출산 {days_overdue}일 지연! 즉시 수의사 연락 필요 🚨🚨"
                action = "즉시 수의사 연락 및 상태 확인"
            elif days_overdue >= 3:
                priority = "urgent"
                message = f"출산 {days_overdue}일 지연! 긴급 확인 필요 🚨"
                action = "집중 관찰 및 수의사 상담 고려"
            else:
                priority = "high"
                message = f"출산 {days_overdue}일 지연, 집중 관찰 필요"
                action = "24시간 관찰 및 이상 증상 체크"
            
            birth_overdue_list.append({
                "cattle_id": record.cattle_id,
                "cattle_number": cattle.identification_number if cattle else "Unknown",
                "breeding_id": record.id,
                "expected_date": record.expected_calving_date,
                "days_overdue": days_overdue,
                "message": message,
                "priority": priority,
                "action": action
            })
        
        return birth_overdue_list
    
    # ============================================
    # 전체 이벤트 요약
    # ============================================
    
    def get_all_events_summary(self) -> Dict[str, List[Dict]]:
        """
        모든 이벤트 요약 (대시보드용)
        
        Returns:
            5가지 이벤트 타입별 리스트
        """
        return {
            "breeding_due": self.calculate_breeding_due(),
            "estrus_check": self.calculate_estrus_check(),
            "pregnancy_check": self.calculate_pregnancy_check(),
            "birth_due": self.calculate_birth_due(),
            "birth_overdue": self.calculate_birth_overdue()
        }
    
    def get_event_counts(self) -> Dict[str, int]:
        """
        이벤트 개수 요약
        
        Returns:
            각 이벤트 타입별 개수
        """
        return {
            "breeding_due_count": len(self.calculate_breeding_due()),
            "estrus_check_count": len(self.calculate_estrus_check()),
            "pregnancy_check_count": len(self.calculate_pregnancy_check()),
            "birth_due_count": len(self.calculate_birth_due()),
            "birth_overdue_count": len(self.calculate_birth_overdue())
        }
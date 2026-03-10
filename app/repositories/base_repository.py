"""
Base Repository
모든 Repository가 상속받을 기본 CRUD 기능 제공
"""
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from app.database import Base

# Generic Type 정의
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    기본 Repository 클래스
    공통 CRUD 기능 제공
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Args:
            model: SQLAlchemy 모델 클래스
            db: 데이터베이스 세션
        """
        self.model = model
        self.db = db
    
    # ============================================
    # Create
    # ============================================
    
    def create(self, obj_in: dict) -> ModelType:
        """
        새 레코드 생성
        
        Args:
            obj_in: 생성할 데이터 (dict)
        
        Returns:
            생성된 모델 인스턴스
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    # ============================================
    # Read
    # ============================================
    
    def get(self, id: int) -> Optional[ModelType]:
        """
        ID로 단일 레코드 조회
        
        Args:
            id: 조회할 ID
        
        Returns:
            모델 인스턴스 또는 None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[ModelType]:
        """
        여러 레코드 조회 (페이지네이션 지원)
        
        Args:
            skip: 건너뛸 개수
            limit: 가져올 개수
            filters: 필터 조건 (dict)
        
        Returns:
            모델 인스턴스 리스트
        """
        query = self.db.query(self.model)
        
        # 필터 적용
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def get_all(self, filters: Optional[dict] = None) -> List[ModelType]:
        """
        모든 레코드 조회 (페이지네이션 없음)
        
        Args:
            filters: 필터 조건 (dict)
        
        Returns:
            모든 모델 인스턴스 리스트
        """
        query = self.db.query(self.model)
        
        # 필터 적용
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.all()
    
    def count(self, filters: Optional[dict] = None) -> int:
        """
        레코드 개수 조회
        
        Args:
            filters: 필터 조건 (dict)
        
        Returns:
            레코드 개수
        """
        query = self.db.query(self.model)
        
        # 필터 적용
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    # ============================================
    # Update
    # ============================================
    
    def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        """
        레코드 수정
        
        Args:
            id: 수정할 ID
            obj_in: 수정할 데이터 (dict)
        
        Returns:
            수정된 모델 인스턴스 또는 None
        """
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        # 수정할 필드만 업데이트
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    # ============================================
    # Delete
    # ============================================
    
    def delete(self, id: int) -> bool:
        """
        레코드 삭제
        
        Args:
            id: 삭제할 ID
        
        Returns:
            삭제 성공 여부
        """
        db_obj = self.get(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    # ============================================
    # Utility
    # ============================================
    
    def exists(self, id: int) -> bool:
        """
        레코드 존재 확인
        
        Args:
            id: 확인할 ID
        
        Returns:
            존재 여부
        """
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
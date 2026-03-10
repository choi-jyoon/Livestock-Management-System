from sqlalchemy import Column, Integer, String, Date, Text, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from .mixins import TimestampMixin
import enum

class NoteTypeEnum(str, enum.Enum):
    SYMPTOM = "SYMPTOM"  # 증상
    TREATMENT = "TREATMENT"  # 투약/치료
    BIRTH = "BIRTH"  # 출산
    OTHER = "OTHER"  # 기타

class CattleNote(Base, TimestampMixin):
    __tablename__ = "cattle_notes"

    id = Column(Integer, primary_key=True, index=True)
    cattle_id = Column(Integer, ForeignKey("cattle.id"), nullable=False)
    note_date = Column(Date, nullable=False)
    note_type = Column(SQLEnum(NoteTypeEnum), default=NoteTypeEnum.OTHER, nullable=False)
    content = Column(Text, nullable=False)  # Text로 변경 (긴 내용 가능)
    is_active = Column(Boolean, default=True, nullable=False)  # 활성화 여부

    cattle = relationship("Cattle", back_populates="notes")

    def __repr__(self):
        return f"<CattleNote(id={self.id}, cattle_id={self.cattle_id}, date={self.note_date}, type={self.note_type.value})>"
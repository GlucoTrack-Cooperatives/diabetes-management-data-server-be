import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dao.model.User import Base

class GlucoseReading(Base):
    __tablename__ = "glucose_reading"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patient.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Integer, nullable=False)
    trend = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False, default="dexcom")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="glucose_readings")
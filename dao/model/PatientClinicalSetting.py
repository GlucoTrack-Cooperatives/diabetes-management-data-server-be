import uuid
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dao.model.User import Base


class PatientClinicalSetting(Base):
    __tablename__ = "patient_clinical_setting"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patient.id'), nullable=False, unique=True)

    target_range_low = Column(Integer, nullable=False)
    target_range_high = Column(Integer, nullable=False)

    insulin_carb_ratio = Column(Float, nullable=False)
    correction_factor = Column(Float, nullable=False)

    low_threshold = Column(Integer, nullable=False, default=70)
    high_threshold = Column(Integer, nullable=False, default=200)

    patient = relationship("Patient", back_populates="clinical_setting")
from sqlalchemy import Column, ForeignKey, String, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from dao.model.User import User

class Patient(User):
    __tablename__ = "patient"

    id = Column(UUID(as_uuid=True), ForeignKey('user.id'), primary_key=True)

    phone_numbers = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    diagnosis_date = Column(Date, nullable=False)
    emergency_contact_phone = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    dexcom_email = Column(String(255), nullable=True)
    dexcom_password = Column(String(255), nullable=True)

    glucose_readings = relationship("GlucoseReading", back_populates="patient")
    clinical_setting = relationship("PatientClinicalSetting", back_populates="patient", uselist=False)
    alerts = relationship("Alert", back_populates="patient")

    __mapper_args__ = {
        'polymorphic_identity': 'PATIENT',
    }
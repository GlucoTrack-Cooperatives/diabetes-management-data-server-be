import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    email = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    creation_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    modification_timestamp = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __mapper_args__ = {
        'polymorphic_identity': 'USER',
        'polymorphic_on': role
    }

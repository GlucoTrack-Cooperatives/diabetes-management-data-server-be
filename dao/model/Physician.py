from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from dao.model.User import User

class Physician(User):
    __tablename__ = "physician"

    id = Column(UUID(as_uuid=True), ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'PHYSICIAN',
    }
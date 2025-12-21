from typing import Type

from sqlalchemy.orm import Session
import uuid

from dao.model.User import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self) -> list[Type[User]]:
        return self.db.query(User).all()

    def get_user_by_uuid(self, user_uuid: str) -> User | None:
        return self.db.query(User).filter(User.id == uuid.UUID(user_uuid)).first()

    def save_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

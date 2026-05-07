from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import UserCreate


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_user_by_handle(self, handle: str) -> User | None:
        statement = select(User).where(User.handle == handle)
        return self.db.scalar(statement)

    def create_user(self, user_in: UserCreate) -> User:
        user = User(**user_in.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

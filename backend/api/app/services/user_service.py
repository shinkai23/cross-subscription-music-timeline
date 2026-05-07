from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate


class DuplicateUserHandleError(Exception):
    pass


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create_user(self, user_in: UserCreate) -> User:
        existing_user = self.repository.get_user_by_handle(user_in.handle)
        if existing_user is not None:
            raise DuplicateUserHandleError

        return self.repository.create_user(user_in)

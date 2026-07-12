from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.repositories.service_account_repository import ServiceAccountRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import (
    ProviderAccountRead,
    ProviderAccountsRead,
    UserCreate,
    UserRead,
)
from app.services.user_service import DuplicateUserHandleError, UserService


router = APIRouter(tags=["users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    service: UserService = Depends(get_user_service),
) -> User:
    try:
        return service.create_user(user_in)
    except DuplicateUserHandleError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User handle already exists",
        ) from exc


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/me/provider-accounts", response_model=ProviderAccountsRead)
def read_my_provider_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProviderAccountsRead:
    repository = ServiceAccountRepository(db)
    service_accounts = repository.list_connected_by_user_id(current_user.id)
    return ProviderAccountsRead(
        items=[
            ProviderAccountRead(
                provider=service_account.provider,
                provider_user_id=service_account.provider_user_id,
                connected=True,
                created_at=service_account.created_at,
            )
            for service_account in service_accounts
        ]
    )

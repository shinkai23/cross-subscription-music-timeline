from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.dependencies.db import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import DevLoginRequest, TokenRead


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/dev-login", response_model=TokenRead)
def dev_login(
    request: DevLoginRequest,
    db: Session = Depends(get_db),
) -> TokenRead:
    user = UserRepository(db).get_user_by_handle(request.handle)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return TokenRead(access_token=create_access_token(subject=user.id))

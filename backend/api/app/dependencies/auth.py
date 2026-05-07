from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import InvalidTokenError, decode_access_token
from app.dependencies.db import get_db
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_subject(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_access_token(token)
    except InvalidTokenError as exc:
        raise _credentials_exception() from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise _credentials_exception()

    return subject


def get_current_user(
    subject: str = Depends(get_current_subject),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, subject)
    if user is None:
        raise _credentials_exception()

    return user


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.repositories.service_account_repository import ServiceAccountRepository
from app.schemas.apple_music_schema import (
    AppleMusicConnectRequest,
    AppleMusicConnectResponse,
)
from app.services.service_account_errors import ServiceAccountAlreadyConnectedError
from app.services.service_account_service import ServiceAccountService
from app.services.token_encryption_service import TokenEncryptionService

router = APIRouter(prefix="/auth/apple-music", tags=["apple-music-auth"])


def get_service_account_service(
    db: Session = Depends(get_db),
) -> ServiceAccountService:
    return ServiceAccountService(
        repository=ServiceAccountRepository(db),
        token_encryption_service=TokenEncryptionService(),
    )


@router.post("/connect", response_model=AppleMusicConnectResponse)
async def connect_apple_music(
    request: AppleMusicConnectRequest,
    current_user: User = Depends(get_current_user),
    service: ServiceAccountService = Depends(get_service_account_service),
) -> AppleMusicConnectResponse:
    try:
        service.connect_apple_music_account(
            user=current_user,
            provider_user_id=request.provider_user_id,
            music_user_token=request.music_user_token,
        )
    except ServiceAccountAlreadyConnectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Apple Music account is already connected",
        ) from exc

    return AppleMusicConnectResponse(
        provider="apple_music",
        connected=True,
    )

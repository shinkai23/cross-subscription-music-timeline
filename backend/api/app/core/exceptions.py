from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.providers.error import ProviderApiError


async def provider_api_error_handler(
    request: Request,
    exc: ProviderApiError,
) -> JSONResponse:
    if exc.status_code in {401, 403, 404, 429}:
        status_code = exc.status_code
    else:
        status_code = status.HTTP_502_BAD_GATEWAY
    
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": {
                "provider": exc.provider,
                "message": exc.message,
            }
        },
    )

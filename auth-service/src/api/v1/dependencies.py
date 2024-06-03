from uuid import UUID
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from services.auth_service import get_auth_service, AuthService

_TOKEN_PREFIX = 'Bearer '


def get_token(authorization: Annotated[str | None, Header()] = None) -> str:
    token = (authorization.removeprefix(_TOKEN_PREFIX)
             if authorization and authorization.startswith(_TOKEN_PREFIX)
             else '')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


async def get_request_user_id(
    access_token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UUID:
    if await auth_service.is_access_token_invalid(access_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid access token")
    return auth_service.get_user_id(access_token)

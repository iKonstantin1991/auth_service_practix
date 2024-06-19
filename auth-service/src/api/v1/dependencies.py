from uuid import UUID
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from services.auth_service import get_auth_service, AuthService
from services.role_service import RoleService, get_role_service
from services.user_service import UserService, get_user_service

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
    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid access token')
    return auth_service.get_user_id_from_access_token(access_token)


async def revoke_tokens(
    refresh_token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> None:
    if not await auth_service.check_is_valid_and_remove_refresh_token(refresh_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid refresh token')
    await auth_service.logout(refresh_token)


async def check_user_staff(
        request_user_id: Annotated[UUID, Depends(get_request_user_id)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        role_service: Annotated[RoleService, Depends(get_role_service)],
):
    user_roles = await user_service.get_roles(request_user_id)
    if not await role_service.is_staff(user_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not have permission')

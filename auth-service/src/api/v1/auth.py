from uuid import UUID
from typing import List, Annotated

from fastapi import APIRouter, Depends, Response, Header, HTTPException, status

from services.auth_service import get_auth_service, AuthService
from services.user_service import get_user_service, UserService
from api.v1.dependencies import get_token, get_request_user_id
from api.v1.schemas import UserIn, UserOut, UserCredentials, Token, AuthHistory

router = APIRouter()


@router.post('/signup', response_model=UserOut)
async def signup(
    new_user: UserIn,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserOut:
    if await user_service.get_by_email(new_user.email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exists")
    return await user_service.create(new_user.email, new_user.password)


@router.post('/login', response_model=Token)
async def login(
    user_credentials: UserCredentials,
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_agent: Annotated[str | None, Header()] = None,
) -> Token:
    user = await user_service.get_by_email(user_credentials.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not auth_service.verify_password(user_credentials.email, user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")
    access_token = auth_service.create_access_token(user.id)
    refresh_token = await auth_service.create_refresh_token(user.id)
    await auth_service.update_history(user.id, user_agent)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post('/logout')
async def logout(
    access_token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Response:
    if await auth_service.is_access_token_invalid(access_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid access token")
    await auth_service.invalidate_access_token(access_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/refresh', response_model=Token)
async def refresh(
    refresh_token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    if await auth_service.is_refresh_token_invalid(refresh_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token")
    user_id = auth_service.get_user_id(refresh_token)
    access_token = auth_service.create_access_token(user_id)
    refresh_token = await auth_service.create_refresh_token(user_id)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get('/history', response_model=List[AuthHistory])
async def history(
    request_user_id: Annotated[UUID, Depends(get_request_user_id)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> List[AuthHistory]:
    return await auth_service.get_history(request_user_id)

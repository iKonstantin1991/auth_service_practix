from typing import Annotated

from fastapi import APIRouter, Depends, Header
from fastapi.responses import RedirectResponse

from core.config import settings
from services.user_service import get_user_service, UserService
from services.auth_service import get_auth_service, AuthService
from api.v1.schemas import Token

router = APIRouter()


@router.get('/redirect')
async def redirect() -> RedirectResponse:
    return RedirectResponse('https://oauth.yandex.ru/authorize?'
                            'response_type=code&'
                            f'client_id={settings.yandex_client_id}')


@router.get('/tokens', response_model=Token)
async def get_tokens(
    code: str,
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_agent: Annotated[str | None, Header()] = None,
) -> Token:
    user = await user_service.get_or_create_from_yandex(code)
    access_token, refresh_token = await auth_service.create_token_pair(user.id, user.roles)
    await auth_service.update_history(user.id, user_agent)
    return Token(access_token=access_token, refresh_token=refresh_token)

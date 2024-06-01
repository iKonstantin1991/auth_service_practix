from typing import List
from uuid import UUID

from fastapi import Depends
from services.password_service import PasswordService, get_password_service
class AuthService:
    def __init__(self, password_service: PasswordService):
        self.password_service = password_service

    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # settings
    ALGORITHM = "HS256"

    def create_access_token(self, data: dict) -> str:
        return _create_token(data, timedelta(minutes=60))


    await def create_refresh_token(self, data: dict) -> str:
        # add to cache
        return _create_token(data, timedelta(days=10))


    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass

    async def access_token_invalid(self, access_token: str) -> bool:
        pass

    async def refresh_token_invalid(self, refresh_token: str) -> bool:
        # check refresh token is valid
        # getdel refresh token from cache
        pass

    async def invalidate_access_token(self, access_token: str) -> None:
        pass

    async def get_history(self, user_id: UUID) -> List[UserLogin]:
        pass    

    async def update_history(self, user_id: UUID, user_agent: str) -> None:
        pass

    def _create_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        to_encode.update({"exp": datetime.now() + expires_delta})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


def get_auth_service(password_service: PasswordService = Depends(get_password_service),) -> AuthService:
    return AuthService(password_service)

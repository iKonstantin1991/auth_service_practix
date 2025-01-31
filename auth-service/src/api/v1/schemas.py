from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCredentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)


class UserIn(UserCredentials):
    pass


class UserOut(BaseModel):
    id: UUID
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str


class AuthHistory(BaseModel):
    user_agent: str
    date: datetime

    class Config:
        from_attributes = True


class RoleIn(BaseModel):
    name: str


class RoleOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

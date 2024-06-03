import uuid
from typing import List
from datetime import datetime

from sqlalchemy import Column, Table, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import declarative_base


Base = declarative_base()


user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('role_id', ForeignKey('roles.id'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(insert_default=func.now())  # pylint: disable=not-callable
    logins: Mapped[List['UserLogin']] = relationship(back_populates='user')
    roles: Mapped[List['Role']] = relationship(secondary=user_role, back_populates='users')

    def __repr__(self) -> str:
        return f'<User {self.email}>'


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    created: Mapped[datetime] = mapped_column(insert_default=func.now())  # pylint: disable=not-callable
    users: Mapped[List['User']] = relationship(secondary=user_role, back_populates='roles')

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class UserLogin(Base):
    __tablename__ = 'user_logins'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_agent: Mapped[str | None]
    date: Mapped[datetime] = mapped_column(nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='logins')

    def __repr__(self) -> str:
        return f'<UserLogin {self.id}>'

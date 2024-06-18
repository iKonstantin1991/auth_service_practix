import uuid
from typing import List
from datetime import datetime

from sqlalchemy import Column, Table, ForeignKey, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base

user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    created: Mapped[datetime] = mapped_column(insert_default=func.now())  # pylint: disable=not-callable
    logins: Mapped[List['UserLogin']] = relationship(back_populates='user')
    roles: Mapped[List['Role']] = relationship(secondary=user_role, back_populates='users')

    def __repr__(self) -> str:
        return f'<User {self.email}>'


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created: Mapped[datetime] = mapped_column(insert_default=func.now())  # pylint: disable=not-callable
    users: Mapped[List['User']] = relationship(secondary=user_role, back_populates='roles')

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class YandexUser(Base):
    __tablename__ = 'yandex_users'

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f'<YandexUser {self.id}>'


class UserLogin(Base):
    __tablename__ = 'user_logins'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
        }
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_agent: Mapped[str | None] = mapped_column(Text)
    user_device_type: Mapped[str] = mapped_column(Text, primary_key=True)
    date: Mapped[datetime] = mapped_column(nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(back_populates='logins')

    def __repr__(self) -> str:
        return f'<UserLogin {self.id}>'

from uuid import uuid4, UUID
from typing import List

from fastapi import Depends
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas import RoleIn, RoleOut

from models.entity import Role
from db.postgres import get_session


class RoleService:
    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    STAFF_ROLES = ['superuser', 'admin', 'service']
    EXISTING_ROLES = STAFF_ROLES + ['user']

    async def is_staff(self, user_roles: List[Role]) -> bool:
        user_roles_names = [user_role.name for user_role in user_roles]
        for staff_role in self.STAFF_ROLES:
            if (
                staff_role in user_roles_names
                and await self.is_role_exists_by_name(staff_role)
            ):
                return True
        return False

    async def get(self) -> List[Role]:
        roles = await self.async_session.execute(select(Role))
        roles = roles.scalars().all()
        return roles

    async def is_role_exists_by_name(self, new_role_name: str) -> bool:
        role = await self.async_session.execute(
            select(Role).where(Role.name == new_role_name)
        )
        role = role.scalars().all()
        return bool(role)

    async def is_role_exists_by_id(self, role_id: UUID) -> bool:
        role = await self.async_session.execute(
            select(Role).where(Role.id == role_id)
        )
        role = role.scalars().all()
        if role:
            return True
        return False

    async def create(self, new_role: RoleIn) -> RoleOut:
        role_id = uuid4()
        await self.async_session.execute(
            insert(Role).values(id=role_id, name=new_role.name)
        )
        await self.async_session.commit()
        return RoleOut(id=role_id, name=new_role.name)

    async def delete(self, role_id: UUID):
        await self.async_session.execute(
            delete(Role).where(Role.id == role_id)
        )
        await self.async_session.commit()

    async def get_role_by_id(self, role_id: UUID) -> Role:
        return await self.async_session.scalar(
            select(Role).where(Role.id == role_id)
        )


def get_role_service(
    async_session: AsyncSession = Depends(get_session),
) -> RoleService:
    return RoleService(async_session)

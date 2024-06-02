import uuid
from typing import List

from api.v1.schemas import RoleIn, RoleOut
from fastapi import Depends
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.entity import Role
from db.postgres import get_session


class RoleService:
    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    STAFF_ROLES = ['superuser', 'admin']
    EXISTING_ROLES = STAFF_ROLES + ['user']

    async def is_staff(self, user_roles) -> bool:
        for staff_role in self.STAFF_ROLES:
            if staff_role in user_roles and await self.is_role_exists(RoleIn(name=staff_role)):
                return True
        return False

    async def get(self) -> List[RoleOut]:
        roles = await self.async_session.execute(select(Role))
        roles = roles.scalars().all()
        roles_out = []
        for role in roles:
            roles_out.append(RoleOut(id=role.id, name=role.name))
        return roles_out

    async def is_role_exists(self, new_role: RoleIn) -> bool:
        role = await self.async_session.execute(select(Role).where(Role.name == new_role.name))
        role = role.scalars().all()
        if role:
            return True
        return False

    async def create(self, new_role: RoleIn) -> RoleOut:
        role_id = uuid.uuid4()
        await self.async_session.execute(insert(Role).values(id=role_id, name=new_role.name))
        await self.async_session.commit()
        return RoleOut(id=role_id, name=new_role.name)

    async def delete(self, role_id: str):
        await self.async_session.execute(delete(Role).where(Role.id == role_id))
        await self.async_session.commit()


def get_role_service(
        async_session: AsyncSession = Depends(get_session),
) -> RoleService:
    return RoleService(async_session)

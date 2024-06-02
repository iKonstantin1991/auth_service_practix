from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from services.role_service import RoleService, get_role_service
from services.user_service import UserService, get_user_service


async def check_user_authorization(
        request_user_id: Annotated[UUID, Depends(get_request_user_id)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        role_service: Annotated[RoleService, Depends(get_role_service)],
):
    user_roles = await user_service.get_roles(request_user_id)
    if not await role_service.is_staff(user_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")

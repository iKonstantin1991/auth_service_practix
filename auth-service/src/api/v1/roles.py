from uuid import uuid4, UUID
from typing import List, Annotated

from fastapi import APIRouter, Response, status, Depends, HTTPException

from api.v1.schemas import RoleIn, RoleOut
from services.role_service import RoleService, get_role_service

router = APIRouter()


@router.get('/', response_model=List[RoleOut])
async def get_roles(
        request_user_id: Annotated[UUID, Depends(get_request_user_id)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        role_service: Annotated[RoleService, Depends(get_role_service)],
) -> List[RoleOut]:
    user_roles = await user_service.get_roles(request_user_id)
    if role_service.is_staff(user_roles):
        return await role_service.get()
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")


@router.post('/', response_model=RoleOut)
async def create_role(
        new_role: RoleIn,
        access_token: str,
        request_user_id: Annotated[UUID, Depends(get_request_user_id)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        role_service: Annotated[RoleService, Depends(get_role_service)],
) -> RoleOut:
    # check access token
    if not valid - return 401 - unauthorized
    get user roles
    user_roles = await user_service.get_roles(request_user_id)
    if not role_service.is_staff(user_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")
    if await role_service.is_role_exists(new_role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Role {new_role.name} already exists')
    new_role = await role_service.create(new_role)
    return new_role


@router.delete('/{role_id}')
async def delete_role(
        role_id: str,
        access_token: str,
        user_service: Annotated[UserService, Depends(get_user_service)],
        role_service: Annotated[RoleService, Depends(get_role_service)],
) -> Response:
    # check access token
    user_roles = await user_service.get_roles(request_user_id)
    if not role_service.is_staff(user_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")
    await role_service.delete(role_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

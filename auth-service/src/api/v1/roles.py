from typing import List, Annotated

from fastapi import APIRouter, Response, status, Depends, HTTPException

from api.v1.schemas import RoleIn, RoleOut
from api.v1.dependencies import check_user_staff
from services.role_service import RoleService, get_role_service

router = APIRouter()


@router.get('/', response_model=List[RoleOut], dependencies=[Depends(check_user_staff)])
async def get_roles(
        role_service: Annotated[RoleService, Depends(get_role_service)],
) -> List[RoleOut]:
    return await role_service.get()


@router.post('/', response_model=RoleOut, dependencies=[Depends(check_user_staff)])
async def create_role(
        new_role: RoleIn,
        role_service: Annotated[RoleService, Depends(get_role_service)],
) -> RoleOut:
    if await role_service.is_role_exists_by_name(new_role.name):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Role {new_role.name} already exists')
    new_role = await role_service.create(new_role)
    return new_role


@router.delete('/{role_id}', dependencies=[Depends(check_user_staff)])
async def delete_role(
        role_id: str,
        role_service: Annotated[RoleService, Depends(get_role_service)],
) -> Response:
    await role_service.delete(role_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from typing import List, Annotated

from fastapi import APIRouter, Response, status, Depends, HTTPException

from api.v1.schemas import RoleIn, RoleOut
from api.v1.dependencies import check_user_authorization, get_token
from services.role_service import RoleService, get_role_service
from services.auth_service import AuthService, get_auth_service

router = APIRouter()


@router.get('/', response_model=List[RoleOut])
async def get_roles(
        role_service: Annotated[RoleService, Depends(get_role_service)],
        check_user_authorization: Annotated[None, Depends(check_user_authorization)],
) -> List[RoleOut]:
    return await role_service.get()


@router.post('/', response_model=RoleOut)
async def create_role(
        new_role: RoleIn,
        access_token: Annotated[str, Depends(get_token)],
        role_service: Annotated[RoleService, Depends(get_role_service)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        check_user_authorization: Annotated[None, Depends(check_user_authorization)],
) -> RoleOut:
    if await auth_service.access_token_invalid(access_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid access token')
    if await role_service.is_role_exists(new_role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Role {new_role.name} already exists')
    new_role = await role_service.create(new_role)
    return new_role


@router.delete('/{role_id}')
async def delete_role(
        role_id: str,
        access_token: Annotated[str, Depends(get_token)],
        role_service: Annotated[RoleService, Depends(get_role_service)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        check_user_authorization: Annotated[None, Depends(check_user_authorization)],
) -> Response:
    if await auth_service.access_token_invalid(access_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid access token')
    await role_service.delete(role_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from uuid import UUID
from typing import List, Annotated

from fastapi import APIRouter, Response, status, Depends, HTTPException

from api.v1.schemas import UserIn, UserOut, RoleOut
from api.v1.dependencies import get_request_user_id, check_user_staff
from services.user_service import UserService, get_user_service
from services.role_service import RoleService, get_role_service

router = APIRouter()


@router.get('/{user_id}', response_model=UserOut)
async def get_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    request_user_id: Annotated[UUID, Depends(get_request_user_id)],
) -> UserOut:
    if user_id != request_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )

    return await user_service.get_by_id(user_id)


@router.put('/{user_id}', response_model=UserOut)
async def update_user(
    user_id: UUID,
    user: UserIn,
    user_service: Annotated[UserService, Depends(get_user_service)],
    request_user_id: Annotated[UUID, Depends(get_request_user_id)],
) -> UserOut:
    if user_id != request_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )

    return await user_service.update(
        user_id=user_id, email=user.email, password=user.password
    )


@router.get('/{user_id}/roles', response_model=List[RoleOut])
async def get_user_roles(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    request_user_id: Annotated[UUID, Depends(get_request_user_id)],
) -> List[RoleOut]:
    if user_id != request_user_id and not await role_service.is_staff(
        await user_service.get_roles(request_user_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )

    return await user_service.get_roles(user_id)


@router.post(
    '/{user_id}/roles',
    response_model=RoleOut,
    dependencies=[Depends(check_user_staff)],
)
async def assign_role(
    user_id: UUID,
    role_id: UUID,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> RoleOut:
    if not await role_service.is_role_exists_by_id(role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Role not found'
        )

    if await user_service.has_role(user_id=user_id, role_id=role_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User already has this role',
        )

    role_id = await user_service.add_role_to_user(
        user_id=user_id, role_id=role_id
    )
    return await role_service.get_role_by_id(role_id)


@router.delete('/{user_id}/roles', dependencies=[Depends(check_user_staff)])
async def dissociate_role(
    user_id: UUID,
    role_id: UUID,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> Response:
    if not await role_service.is_role_exists_by_id(role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Role not found'
        )

    await user_service.delete_role_from_user(user_id, role_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

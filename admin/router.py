from fastapi import APIRouter, Depends
from users import schemas as user_schema
from auth import schemas as auth_schema
from utils import jwtUtil
from admin import crud
from utils.dbUtil import get_db
from sqlalchemy.orm import Session
from uuid import UUID


router = APIRouter(prefix="/api/v1")


@router.get("/Admin/User/")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
):
    if currentUser.role == "Admin":
        return await crud.get_all_users(db, skip, limit)
    return "No Admin right!"


@router.patch("/Admin/user/{user_id}")
async def update_user(
    request: user_schema.UpdateUser,
    user_id: UUID,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    # Update user
    if currentUser.role == "Admin":
        user_data = await crud.find_existed_user_by_id(db, user_id)
        user = auth_schema.UserList(
            user_id=user_data.user_id,
            email=user_data.email,
            fullname=user_data.fullname,
            phone_number=user_data.phone_number,
            state=user_data.state,
            city=user_data.city,
            created_on=user_data.created_on,
            status=user_data.status,
            verify=user_data.verify,
            role=user_data.role,
        )
        await crud.update_user_admin(db, request, user)
        return {"status_code": 200, "detail": "User updated successfully"}
    return "No Admin right!"


@router.delete("/Admin/User/{user_id}")
async def delete_users(
    user_id: UUID,
    db: Session = Depends(get_db),
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
):
    if currentUser.role == "Admin":
        return await crud.deleate_user(db, user_id)
    return "No Admin right!"

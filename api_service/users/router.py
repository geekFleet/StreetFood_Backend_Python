from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from users import schemas as user_schema
from auth import schemas as auth_schema
from utils import cryptoUtil, jwtUtil
from users import crud as user_crud
from auth import crud as auth_crud
from utils.dbUtil import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1")


@router.get("/user/profile", response_model=auth_schema.UserList)
async def get_user_profile(
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_user),
):
    return currentUser


@router.patch("/user/profile")
async def update_user(
    request: user_schema.UpdateUser,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    # Update user
    await user_crud.update_user(db, request, currentUser)
    return {"status_code": 200, "detail": "User updated successfully"}


@router.delete("/user/profile")
async def deactivate_account(
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    # Delete user
    await user_crud.deactivate_user(db, currentUser)
    return {"status_code": 200, "detail": "User account deactivated successfully"}


@router.get("/user/get-profile-image")
async def get_profile_image(
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
):
    return {"detail": "Todo"}


@router.patch("/user/upload-profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
):
    return "Todo"


@router.post("/user/change-password")
async def change_password(
    chgPwd: auth_schema.ChangePassword,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    user = await auth_crud.get_user(db, currentUser.phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    valid = cryptoUtil.verify_password(chgPwd.old_password, user.password)
    if not valid:
        raise HTTPException(status_code=404, detail="Old password is not match")

    if chgPwd.new_password != chgPwd.confirm_password:
        raise HTTPException(status_code=404, detail="New password is not match.")

    # Change Password
    await user_crud.change_password(db, chgPwd, currentUser)
    return {"status_code": 200, "detail": "Operating successfully"}


@router.get("/user/logout")
async def logout(
    token: str = Depends(jwtUtil.get_token_user),
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    await user_crud.set_logout_list(db, token, currentUser)
    return {"message": "you logged out successfully"}

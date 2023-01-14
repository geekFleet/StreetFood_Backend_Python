import os
import logging
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from users import schemas as user_schema
from auth import schemas as auth_schema
from utils import cryptoUtil, jwtUtil, azur_blob
from users import crud as user_crud
from auth import crud as auth_crud
from utils.dbUtil import get_db
from sqlalchemy.orm import Session
from uuid import UUID


router = APIRouter(prefix="/api/v1")


@router.get("/user/profile")
async def get_user_profile(
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_user),
):
    return {
        "code": 200,
        "detail": "",
        "data": {"user_info": currentUser},
    }


@router.patch("/user/profile")
async def update_user(
    request: user_schema.UpdateUser,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    # Update user
    await user_crud.update_user(db, request, currentUser)
    return {"code": 200, "detail": "User updated successfully"}


@router.delete("/user/profile")
async def deactivate_account(
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    # Delete user
    await user_crud.deactivate_user(db, currentUser)
    return {"code": 200, "detail": "User account deactivated successfully"}


@router.get("/user/get-profile-image")
async def get_profile_image(
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
):

    return {"code": 200, "detail": "Todo"}


@router.patch("/user/upload-profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
):
    try:
        cwd = os.getcwd()
        path_image_dir = "profile-images/"
        full_image_path = os.path.join(cwd, path_image_dir, file.filename)

        # Create directory if not exist
        if not os.path.exists(path_image_dir):
            os.mkdir(path_image_dir)

        # Rename file
        file_name = full_image_path.replace(file.filename, str(currentUser.user_id) + ".jpg")

        # Write file
        with open(file_name, "wb+") as f:
            f.write(file.file.read())
            f.flush()
            f.close()
        obj_azur = azur_blob.azure_blob_file_uploader
        obj_azur.upload_all_images_in_folder()
        return {"code": 200, "detail": "Image uploaded Succesfully!"}

    except Exception as e:
        logging.exception(e)


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
    return {"code": 200, "detail": "Operating successfully"}


@router.get("/user/logout")
async def logout(
    token: str = Depends(jwtUtil.get_token_user),
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    await user_crud.set_logout_list(db, token, currentUser)
    return {"code": 200, "detail": "you logged out successfully"}

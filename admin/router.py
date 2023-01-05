from fastapi import APIRouter, Depends, HTTPException
from users import schemas as user_schema
from auth import schemas as auth_schema
from vendor import schemas as vendor_schema
from review import schemas as review_schema
from utils import jwtUtil
from admin import crud
from vendor import crud as vendor_cud
from review import crud as review_crud
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


@router.get("/Admin/User/{user_id}")
async def get_user_info(
    user_id: UUID,
    db: Session = Depends(get_db),
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
):
    if currentUser.role == "Admin":
        user_data = await crud.find_existed_user_by_id(db, user_id)
        if not user_data:
            return "User Not found"
        return user_data
    return "No Admin right!"


@router.patch("/Admin/user/{user_id}")
async def update_user(
    request: user_schema.AdminUpdateUser,
    user_id: UUID,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    # Update user
    if currentUser.role == "Admin":
        user_data = await crud.find_existed_user_by_id(db, user_id)
        if not user_data:
            return "User Not found"
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
        await crud.deleate_user(db, user_id)
        return "User deleted successfully"
    return "No Admin right!"


@router.patch("/Admin/vendor/{vendor_id}")
async def update_vendor(
    vendor_id: UUID,
    request: vendor_schema.UpdateVendor,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    if currentUser.role == "Admin":
        Vendor = await vendor_cud.find_existed_vendor_by_id(db, vendor_id)
        if not Vendor:
            raise HTTPException(status_code=404, detail="vendor doesnot extist!")
        currentVendor = vendor_schema.UpdateVendor(
            vendor_name=Vendor.vendor_name,
            location=Vendor.location,
            description=Vendor.description,
            morning_timing=Vendor.morning_timing,
            evening_timing=Vendor.evening_timing,
        )
        # Update user
        await vendor_cud.update_vendor(db, vendor_id, request, currentVendor)
        return {"status_code": 200, "detail": "Vendor updated successfully"}
    return "No Admin right!"


@router.delete("/Admin/vendor/delete/{vendor_id}")
async def delete_vendor(
    vendor_id: UUID,
    db: Session = Depends(get_db),
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
):
    if currentUser.role == "Admin":
        return await crud.delete_vendor(db, vendor_id)
    return "No Admin right!"


@router.delete("/Admin/vendor/deactiavte/{vendor_id}")
async def deactivate_vendor(
    vendor_id: UUID,
    db: Session = Depends(get_db),
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
):
    if currentUser.role == "Admin":
        return await crud.deactivate_vendor(db, vendor_id)
    return "No Admin right!"


@router.get("/Admin/review/{vendor_id}/{user_id}")
async def get_review_for_specific_user(
    vendor_id: UUID,
    user_id: UUID,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    if currentUser.role == "Admin":
        review = await review_crud.get_review_by_user_id(db, vendor_id, user_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review doesnot extist!")
        return review
    return "No Admin right!"


@router.patch("/Admin/review/update")
async def update_review(
    vendor_id: UUID,
    user_id: UUID,
    request: review_schema.UpdateReview,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    if currentUser.role == "Admin":
        review = await review_crud.get_review_by_user_id(db, vendor_id, user_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review doesnot extist!")
        currentreview = review_schema.UpdateReview(
            taste=review.taste,
            price_to_quality=review.price_to_quality,
            hygiene=review.hygiene,
            service=review.service,
            description=review.description,
        )
        # Update user
        await review_crud.update_review(db, vendor_id, user_id, request, currentreview)
        overall_rating = (
            review.taste + review.price_to_quality + review.hygiene + review.service
        ) / 4
        await review_crud.update_overall_rating(db, vendor_id, overall_rating, currentUser, user_id)
        return {"status_code": 200, "detail": "Review updated successfully"}
    return "No Admin right!"


@router.delete("/review")
async def delete_review(
    vendor_id: UUID,
    user_id: UUID,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    if currentUser.role == "Admin":
        review = await review_crud.get_review_by_user_id(db, vendor_id, user_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review doesnot extist!")
        # Delete user
        await review_crud.delete_review(db, vendor_id, user_id)
        return {"status_code": 200, "detail": "Review deleted successfully"}
    return "No Admin right!"

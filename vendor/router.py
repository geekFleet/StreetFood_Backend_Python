from fastapi import APIRouter, Depends, HTTPException
from auth import schemas as auth_schema
from utils import jwtUtil
from vendor import schemas
from vendor import crud
from review import crud as review_crud
from review import schemas as review_schemas
from uuid import UUID
from utils.dbUtil import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1")


@router.post("/vendor/register")
async def register(
    user: schemas.RequestVendor,
    review: review_schemas.RequestReview,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):

    existed_vendor = await crud.find_existed_vendor(db, user.vendor_name, user.location)
    if existed_vendor:
        raise HTTPException(status_code=404, detail="vendor already registered!")

    # Create vendor
    await crud.save_vendor(db, user, currentUser)
    vendor = await crud.find_existed_vendor(db, user.vendor_name, user.location)
    overall_rating = (
        review.taste + review.service + review.hygiene + review.price_to_quality
    ) / 4
    await review_crud.save_review(
        db, vendor.vendor_id, review, overall_rating, currentUser
    )
    return {**user.dict()}, {**review.dict()}


@router.patch("/vendor/update")
async def update_user(
    vendor_id: UUID,
    request: schemas.UpdateVendor,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    Vendor = await crud.find_existed_vendor_by_id(db, vendor_id)
    if not Vendor:
        raise HTTPException(status_code=404, detail="vendor doesnot extist!")
    if Vendor.created_by != currentUser.user_id:
        raise HTTPException(status_code=404, detail="No edit right!")
    currentVendor = schemas.UpdateVendor(
        vendor_name=Vendor.vendor_name,
        location=Vendor.location,
        description=Vendor.description,
        morning_timing=Vendor.morning_timing,
        evening_timing=Vendor.evening_timing,
    )
    # Update user
    await crud.update_vendor(db, vendor_id, request, currentVendor)
    return {"status_code": 200, "detail": "Vendor updated successfully"}


@router.get("/vendor/profile/{vendor_id}")
async def get_vendor_profile_by_id(
    vendor_id: UUID,
    db: Session = Depends(get_db),
):
    currentVendor = await crud.find_existed_vendor_by_id(db, vendor_id)

    if not currentVendor:
        raise HTTPException(status_code=404, detail="vendor doesnot extist!")
    return currentVendor


@router.get("/vendor")
async def get_all_vendors(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    vendors = await crud.get_all_vendor(db, skip, limit)
    return vendors

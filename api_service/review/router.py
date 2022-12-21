from fastapi import APIRouter, Depends, HTTPException
from auth import schemas as auth_schema
from utils import jwtUtil
from review import schemas
from review import crud
from vendor import crud as vendor_cud
from uuid import UUID
from utils.dbUtil import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1")


@router.post("/review/register")
async def register(
    vendor_id: UUID,
    review: schemas.RequestReview,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):

    review_row = await crud.get_review_by_user_id(db, vendor_id, currentUser)

    if review_row:
        raise HTTPException(status_code=404, detail="Review already registered!")

    overall_rating = (
        review.taste + review.service + review.hygiene + review.price_to_quality
    ) / 4
    # Create vendor
    await crud.save_review(db, vendor_id, review, overall_rating, currentUser)
    return {**review.dict()}


@router.get("/review")
async def get_review_for_current_user(
    vendor_id: UUID,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    review = await crud.get_review_by_user_id(db, vendor_id, currentUser)
    if not review:
        raise HTTPException(status_code=404, detail="Review doesnot extist!")
    return review


@router.get("/review/vendor")
async def get_overall_review_for_vendor(
    vendor_id: UUID,
    db: Session = Depends(get_db),
):
    row = vendor_cud.find_existed_vendor_by_id(db, vendor_id)
    if not row:
        raise HTTPException(status_code=404, detail="Vendor doesnot extist!")
    overall_taste = await crud.get_avg_taste(db, vendor_id)
    overall_hygine = await crud.get_avg_hygiene(db, vendor_id)
    overall_price_to_quality = await crud.get_avg_price_to_quality(db, vendor_id)
    overall_sevice = await crud.get_avg_service(db, vendor_id)
    overall_rating = await crud.get_avg_overall_rating(db, vendor_id)

    return {
        "overall_taste": overall_taste,
        "overall_hygine": overall_hygine,
        "overall_price_to_quality": overall_price_to_quality,
        "overall_sevice": overall_sevice,
        "overall_rating": overall_rating,
    }


@router.get("/review/all")
async def get_all_review_for_vendor(
    vendor_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    review = await crud.get_all_review(db, vendor_id, skip, limit)
    if not review:
        raise HTTPException(status_code=404, detail="Review doesnot extist!")
    return review


@router.patch("/review/update")
async def update_review(
    vendor_id: UUID,
    request: schemas.UpdateReview,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    review = await crud.get_review_by_user_id(db, vendor_id, currentUser)
    if not review:
        raise HTTPException(status_code=404, detail="Review doesnot extist!")
    currentreview = schemas.UpdateReview(
        taste=review.taste,
        price_to_quality=review.price_to_quality,
        hygiene=review.hygiene,
        service=review.service,
        description=review.description,
    )
    # Update user
    await crud.update_review(db, vendor_id, request, currentreview, currentUser)
    overall_rating = (
        review.taste + review.price_to_quality + review.hygiene + review.service
    ) / 4
    await crud.update_overall_rating(db, vendor_id, overall_rating, currentUser)
    return {"status_code": 200, "detail": "Review updated successfully"}


@router.delete("/review")
async def delete_review(
    vendor_id: UUID,
    currentUser: auth_schema.UserList = Depends(jwtUtil.get_current_active_user),
    db: Session = Depends(get_db),
):
    review = await crud.get_review_by_user_id(db, vendor_id, currentUser)
    if not review:
        raise HTTPException(status_code=404, detail="Review doesnot extist!")
    # Delete user
    await crud.delete_review(db, vendor_id, currentUser)
    return {"status_code": 200, "detail": "Review deleted successfully"}

from sqlalchemy.orm import Session
from sqlalchemy import and_
import models
from uuid import UUID
from review import schemas
from sqlalchemy.sql import func
from auth import schemas as auth_schema


async def save_review(
    db: Session,
    vendor_id: UUID,
    review: schemas.RequestReview,
    overallrating: float,
    currentUser: auth_schema.UserList,
):
    db_item = models.Review(
        vendor_id=vendor_id,
        **review.dict(),
        overall_rating=overallrating,
        created_by=currentUser.user_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


async def get_review_by_user_id(
    db: Session,
    vendor_id: UUID,
    currentUser: auth_schema.UserList,
):
    query = db.query(models.Review).filter(
        and_(
            models.Review.vendor_id == vendor_id,
            models.Review.created_by == currentUser.user_id,
            models.Review.status == True,
        )
    )
    return query.first()


async def get_all_review(db: Session, vendor_id: UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Review)
        .filter(
            and_(models.Review.vendor_id == vendor_id, models.Review.status == True)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


async def get_avg_taste(db: Session, vendor_id: UUID):
    query = db.query(
        func.sum(models.Review.taste).label("overall_taste"),
    ).group_by(models.Review.vendor_id)
    count = (
        db.query(models.Review.taste)
        .filter(
            and_(models.Review.vendor_id == vendor_id, models.Review.status == True)
        )
        .count()
    )
    for _res in query.all():
        return _res.overall_taste / count


async def get_avg_hygiene(db: Session, vendor_id: UUID):
    query = db.query(
        func.sum(models.Review.hygiene).label("overall_hygiene"),
    ).group_by(models.Review.vendor_id)
    count = (
        db.query(models.Review.hygiene)
        .filter(
            and_(models.Review.vendor_id == vendor_id, models.Review.status == True)
        )
        .count()
    )
    for _res in query.all():
        return _res.overall_hygiene / count


async def get_avg_price_to_quality(db: Session, vendor_id: UUID):
    query = db.query(
        func.sum(models.Review.price_to_quality).label("overall_price_to_quality"),
    ).group_by(models.Review.vendor_id)
    count = (
        db.query(models.Review.price_to_quality)
        .filter(
            and_(models.Review.vendor_id == vendor_id, models.Review.status == True)
        )
        .count()
    )
    for _res in query.all():
        return _res.overall_price_to_quality / count


async def get_avg_service(db: Session, vendor_id: UUID):
    query = db.query(
        func.sum(models.Review.service).label("overall_service"),
    ).group_by(models.Review.vendor_id)
    count = (
        db.query(models.Review.service)
        .filter(
            and_(models.Review.vendor_id == vendor_id, models.Review.status == True)
        )
        .count()
    )
    for _res in query.all():
        return _res.overall_service / count


async def get_avg_overall_rating(db: Session, vendor_id: UUID):
    query = db.query(
        func.sum(models.Review.overall_rating).label("overall_rating"),
    ).group_by(models.Review.vendor_id)
    count = (
        db.query(models.Review.overall_rating)
        .filter(
            and_(models.Review.vendor_id == vendor_id, models.Review.status == True)
        )
        .count()
    )
    for _res in query.all():
        return _res.overall_rating / count


async def update_review(
    db: Session,
    vendor_id: UUID,
    request: schemas.UpdateReview,
    currentReview: schemas.UpdateReview,
    currentUser: auth_schema.UserList,
):
    query = (
        db.query(models.Review)
        .filter(
            and_(
                models.Review.vendor_id == vendor_id,
                models.Review.created_by == currentUser.user_id,
                models.Review.status == True,
            )
        )
        .update(
            {
                models.Review.taste: currentReview.taste
                if request.taste is None
                else request.taste,
                models.Review.price_to_quality: currentReview.price_to_quality
                if request.price_to_quality is None
                else request.price_to_quality,
                models.Review.hygiene: currentReview.hygiene
                if request.hygiene is None
                else request.hygiene,
                models.Review.service: currentReview.service
                if request.service is None
                else request.service,
                models.Review.description: currentReview.description
                if request.description is None
                else request.description,
                models.Review.last_updated_on: func.now(),
            }
        )
    )
    db.commit()
    return query


async def update_overall_rating(
    db: Session,
    vendor_id: UUID,
    overall_rating: float,
    currentUser: auth_schema.UserList,
):
    query = (
        db.query(models.Review)
        .filter(
            and_(
                models.Review.vendor_id == vendor_id,
                models.Review.created_by == currentUser.user_id,
                models.Review.status == True,
            )
        )
        .update({models.Review.overall_rating: overall_rating})
    )
    db.commit()

    return query


async def delete_review(
    db: Session, vendor_id: UUID, currentUser: auth_schema.UserList
):
    query = (
        db.query(models.Review)
        .filter(
            and_(
                models.Review.vendor_id == vendor_id,
                models.Review.created_by == currentUser.user_id,
                models.Review.status == True,
            )
        )
        .update({models.Review.status: False})
    )
    db.commit()
    return query

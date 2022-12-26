from sqlalchemy.orm import Session
from sqlalchemy import and_
import models
from uuid import UUID
from vendor import schemas
from sqlalchemy.sql import func
from auth import schemas as auth_schema


async def save_vendor(
    db: Session, user: schemas.RequestVendor, currentUser: auth_schema.UserList
):
    db_item = models.Vendor(
        **user.dict(),
        created_by=currentUser.user_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


async def find_existed_vendor(db: Session, vendor_name: str, location: str):
    query = db.query(models.Vendor).filter(
        and_(
            models.Vendor.vendor_name == vendor_name,
            models.Vendor.location == location,
            models.Vendor.status == True,
        )
    )
    return query.first()


async def find_existed_vendor_by_id(db: Session, vendor_id: UUID):
    query = db.query(models.Vendor).filter(
        and_(models.Vendor.vendor_id == vendor_id, models.Vendor.status == True)
    )
    return query.first()


async def update_vendor(
    db: Session,
    vendor_id: UUID,
    request: schemas.UpdateVendor,
    currentVendor: schemas.UpdateVendor,
):
    query = (
        db.query(models.Vendor)
        .filter(
            and_(models.Vendor.vendor_id == vendor_id, models.Vendor.status == True)
        )
        .update(
            {
                models.Vendor.vendor_name: currentVendor.vendor_name
                if request.vendor_name is None
                else request.vendor_name,
                models.Vendor.location: currentVendor.location
                if request.location is None
                else request.location,
                models.Vendor.description: currentVendor.description
                if request.description is None
                else request.description,
                models.Vendor.morning_timing: currentVendor.morning_timing
                if request.morning_timing is None
                else request.morning_timing,
                models.Vendor.evening_timing: currentVendor.evening_timing
                if request.evening_timing is None
                else request.evening_timing,
                models.Vendor.last_updated_on: func.now(),
            }
        )
    )
    db.commit()
    return query


async def get_all_vendor(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Vendor)
        .filter(models.Vendor.status == True)
        .offset(skip)
        .limit(limit)
        .all()
    )

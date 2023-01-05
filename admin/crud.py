import models
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import and_
from auth import schemas as auth_schema
from users import schemas as user_schema


async def get_all_users(db: Session, skip: int = 0, limit: int = 100):

    query = db.query(models.User).filter(and_(models.User.role == "User"))
    all_user = query.order_by(models.User.last_updated_on).offset(skip).limit(limit).all()
    count = query.count()

    return {"total_count": count, "query": all_user}


async def deleate_user(db: Session, UserId: UUID):
    query = (
        db.query(models.User)
        .filter(
            and_(
                models.User.user_id == UserId,
                models.User.status == True,
            )
        )
        .delete()
    )
    db.commit()
    return query


async def find_existed_user_by_id(db: Session, user_id: UUID):
    query = db.query(models.User).filter(
        and_(models.User.user_id == user_id, models.User.status == True)
    )
    return query.first()


async def update_user_admin(
    db: Session, request: user_schema.AdminUpdateUser, currentUser: auth_schema.UserList
):
    query = (
        db.query(models.User)
        .filter(
            and_(
                models.User.user_id == currentUser.user_id,
                models.User.status == True,
            )
        )
        .update(
            {
                models.User.fullname: currentUser.fullname
                if request.fullname is None
                else request.fullname,
                models.User.state: currentUser.state if request.state is None else request.state,
                models.User.city: currentUser.city if request.city is None else request.city,
                models.User.email: currentUser.email if request.email is None else request.email,
                models.User.status: True if request.status is None else request.status,
            }
        )
    )
    db.commit()
    return query


async def delete_vendor(db: Session, vendor_id: UUID):
    query = (
        db.query(models.Vendor)
        .filter(
            and_(
                models.Vendor.vendor_id == vendor_id,
                models.User.status == True,
            )
        )
        .delete()
    )
    db.commit()
    return query


async def deactivate_vendor(db: Session, vendor_id: UUID):
    query = (
        db.query(models.Vendor)
        .filter(
            and_(
                models.Vendor.vendor_id == vendor_id,
                models.Vendor.status == True,
            )
        )
        .update({models.Vendor.status: False})
    )
    db.commit()
    return query

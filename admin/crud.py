import models
from sqlalchemy.orm import Session
from uuid import UUID
from auth import schemas as auth_schema
from users import schemas as user_schema


async def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.User)
        .filter(models.User.status == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


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
    db: Session, request: user_schema.UpdateUser, currentUser: auth_schema.UserList
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
                models.User.state: currentUser.state
                if request.state is None
                else request.state,
                models.User.city: currentUser.city
                if request.city is None
                else request.city,
                models.User.email: currentUser.email
                if request.email is None
                else request.email,
            }
        )
    )
    db.commit()
    return query

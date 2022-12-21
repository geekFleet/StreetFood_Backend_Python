from sqlalchemy.orm import Session
from utils import cryptoUtil
from sqlalchemy import and_
from users import schemas as user_schema
from auth import schemas as auth_schema
import models


async def update_user(
    db: Session, request: user_schema.UpdateUser, currentUser: auth_schema.UserList
):
    query = (
        db.query(models.User)
        .filter(
            and_(
                models.User.phone_number == currentUser.phone_number,
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


async def deactivate_user(db: Session, currentUser: auth_schema.UserList):
    query = (
        db.query(models.User)
        .filter(
            and_(
                models.User.phone_number == currentUser.phone_number,
                models.User.status == True,
            )
        )
        .update({models.User.state: False})
    )
    db.commit()
    return query


async def change_password(
    db: Session, chgPwd: auth_schema.ChangePassword, currentUser: auth_schema.UserList
):
    query = (
        db.query(models.User)
        .filter(
            and_(
                models.User.phone_number == currentUser.phone_number,
                models.User.status == True,
            )
        )
        .update(
            {models.User.password: cryptoUtil.get_password_hash(chgPwd.new_password)}
        )
    )
    db.commit()
    return query


async def set_logout_list(db: Session, token: str, currentUser: auth_schema.UserList):
    db_item = models.logOutlists(token=token, phone_number=currentUser.phone_number)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

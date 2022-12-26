from sqlalchemy.orm import Session
from sqlalchemy import and_
from auth import schemas
import models


async def create_user(db: Session, user: schemas.UserCreate):
    db_item = models.User(**user.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


async def get_user(db: Session, phone_number: int):
    query = db.query(models.User).filter(
        and_(models.User.phone_number == phone_number, models.User.status == True)
    )
    return query.first()


async def reset_password(db: Session, new_password: str, phone_number: int):
    query = (
        db.query(models.User)
        .filter(
            models.User.phone_number == phone_number,
        )
        .update({models.User.password: new_password})
    )
    db.commit()
    return query


async def find_token_logout_lists(db: Session, token: str):
    query = db.query(models.logOutlists).filter(models.logOutlists.token == token)
    return query.first()


async def verify_user(db: Session, phone_number: int):
    query = (
        db.query(models.User)
        .filter(
            models.User.phone_number == phone_number,
        )
        .update({models.User.verify: True})
    )
    db.commit()
    return query

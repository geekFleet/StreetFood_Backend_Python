from sqlalchemy.orm import Session
from sqlalchemy.sql import text, func
from sqlalchemy import and_
import models
from opts import schemas


async def save_otp(
    db: Session, request: schemas.CreateOTP, session_id: str, otp_code: int
):
    db_item = models.Otp(
        phone_number=request.phone_number, session_id=session_id, otp_code=otp_code
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


async def find_otp_block(db: Session, phone_number: int):
    query = db.query(models.OtpBlock).filter(
        and_(
            models.OtpBlock.phone_number == phone_number,
            models.OtpBlock.created_on >= (func.now() - text("interval '5 minutes'")),
        )
    )
    return query.first()


async def find_otp_life_time(db: Session, phone_number: int, session_id: str):
    query = db.query(models.Otp).filter(
        and_(
            models.Otp.phone_number == phone_number,
            models.Otp.session_id == session_id,
            models.Otp.created_on >= (func.now() - text("interval '10 minutes'")),
        )
    )
    return query.first()


async def save_otp_failed_count(
    db: Session, phone_number: int, session_id: str, otp_code: int
):
    query = (
        db.query(models.Otp)
        .filter(
            and_(
                models.Otp.phone_number == phone_number,
                models.Otp.session_id == session_id,
                models.Otp.otp_code == otp_code,
            )
        )
        .update({models.Otp.otp_failed_count: models.Otp.otp_failed_count + 1})
    )
    db.commit()
    return query


async def save_block_otp(db: Session, phone_number: int):
    db_item = models.OtpBlock(phone_number=phone_number)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


async def disable_otp(db: Session, phone_number: int, session_id: str, otp_code: int):
    query = (
        db.query(models.Otp)
        .filter(
            and_(
                models.Otp.phone_number == phone_number,
                models.Otp.session_id == session_id,
                models.Otp.otp_code == otp_code,
            )
        )
        .update({models.Otp.status: False})
    )
    db.commit()
    return query

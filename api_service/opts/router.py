import uuid
import random
from fastapi import APIRouter, HTTPException, Depends
from opts import schemas
from opts import crud
from utils.dbUtil import get_db
from sqlalchemy.orm import Session
from auth import crud as auth_crud

router = APIRouter(prefix="/api/v1")


@router.post("/otp/send")
async def send_otp(request: schemas.CreateOTP, db: Session = Depends(get_db)):
    # Check if phone number exist in db or Not
    user = await auth_crud.get_user(db, request.phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    # Check block OTP
    opt_blocks = await crud.find_otp_block(db, request.phone_number)
    if opt_blocks:
        raise HTTPException(
            status_code=404, detail="Sorry, this phone number is blocked in 5 minutes"
        )

    # Generate and save to table OTPs
    otp_code = random.randint(1000, 9999)
    session_id = str(uuid.uuid1())
    await crud.save_otp(db, request, session_id, otp_code)

    # # Send OTP to email or phone

    return {
        "code": 200,
        "message": "We've sent an email with instructions to reset your password.",
        "session_id": session_id,
    }


@router.post("/otp/verify")
async def verify_otp(request: schemas.VerifyOTP, db: Session = Depends(get_db)):
    get_user = await auth_crud.get_user(db, request.phone_number)
    if not get_user:
        raise HTTPException(status_code=404, detail="User not found!")
    # Check block OTP
    opt_blocks = await crud.find_otp_block(db, request.phone_number)
    if opt_blocks:
        raise HTTPException(
            status_code=404,
            detail="Sorry, this phone number is blocked in 5 minutes",
        )

    # Check OTP code 4 digit life time
    otp_result = await crud.find_otp_life_time(
        db, request.phone_number, request.session_id
    )
    if not otp_result:
        raise HTTPException(
            status_code=404, detail="OTP code has expired, please request a new one."
        )

    # Check if OTP code is already used
    if otp_result.status is False:
        raise HTTPException(
            status_code=404, detail="OTP code has used, please request a new one."
        )

    # Verify OTP code, if not verified,
    if otp_result.otp_code != request.otp_code:
        # Increment OTP failed count
        await crud.save_otp_failed_count(
            db, otp_result.phone_number, otp_result.session_id, otp_result.otp_code
        )

        # If OTP failed count = 5
        # then block otp
        if otp_result.otp_failed_count + 1 == 5:
            await crud.save_block_otp(db, otp_result.phone_number)
            raise HTTPException(
                status_code=404,
                detail="Sorry, this phone number is blocked in 5 minutes",
            )

        # Throw exceptions
        raise HTTPException(
            status_code=404, detail="The OTP code you've entered is incorrect."
        )

    # Disable otp code when succeed verified
    await crud.disable_otp(
        db, otp_result.phone_number, otp_result.session_id, otp_result.otp_code
    )
    if get_user.verify is False:
        await auth_crud.verify_user(db, request.phone_number)

    return {"status_code": 200, "detail": "OTP verified successfully"}

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth import schemas
from auth import crud

from opts.router import send_otp, verify_otp, schemas as otp_schemas
from utils import cryptoUtil, jwtUtil, constantUtil
from utils.dbUtil import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/v1")


@router.post("/auth/register")
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Checking if user exist in db
    exi_user = await crud.get_user(db, user.phone_number)
    if exi_user:
        raise HTTPException(status_code=400, detail="User already registered!")

    # Create new user
    user.password = cryptoUtil.get_password_hash(user.password)
    await crud.create_user(db, user)
    phone = otp_schemas.CreateOTP(phone_number=user.phone_number)
    result = await send_otp(phone, db)
    return {**user.dict()}, {"session_id": result.get("session_id")}


@router.post("/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # Checking if user exist in db
    user = await crud.get_user(db, phone_number=int(form_data.username))
    if not user:
        raise HTTPException(status_code=400, detail="User not found!")

    # verifying the input passwod and hased password
    is_valid = cryptoUtil.verify_password(form_data.password, user.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Incorrect username or password!")

    access_token_expires = jwtUtil.timedelta(
        minutes=constantUtil.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = await jwtUtil.create_access_token(
        data={"sub": form_data.username},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/forgot-password")
async def forgot_password(
    request: otp_schemas.CreateOTP, db: Session = Depends(get_db)
):
    # Check existed user
    user = await crud.get_user(db, request.phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    # Send otp to registered number/email
    result = await send_otp(request, db)
    return {
        "code": 200,
        "message": "We've sent an email with instructions to reset your password.",
        "session_id": result.get("session_id"),
    }


@router.post("/auth/reset-password")
async def reset_password(
    otp_request: otp_schemas.VerifyOTP,
    request: schemas.ResetPassword,
    db: Session = Depends(get_db),
):
    # Check both new & confirm password are matched
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=404, detail="New password is not match.")

    # Verify Otp
    await verify_otp(otp_request, db)

    # Reset new password
    new_hash_password = cryptoUtil.get_password_hash(request.new_password)
    await crud.reset_password(db, new_hash_password, otp_request.phone_number)
    return {"code": 200, "message": "Password has been reset successfully"}

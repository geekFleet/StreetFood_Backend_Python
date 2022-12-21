import jwt
import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from pydantic import ValidationError
from utils import constantUtil
from sqlalchemy.orm import Session
from utils.dbUtil import get_db
from auth import schemas
from auth import crud

JWT_SECRET_KEY = os.environ["SECRET_KEY"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_token_user(token: str = Depends(oauth2_scheme)):
    return token


async def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=constantUtil.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, JWT_SECRET_KEY, algorithm=constantUtil.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    logout_list = await crud.find_token_logout_lists(db, token)
    if logout_list:
        raise credentials_exception

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[constantUtil.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(phone_number=username)
    except (PyJWTError, ValidationError):
        raise credentials_exception

    user = await crud.get_user(db, token_data.phone_number)
    if user is None:
        raise credentials_exception
    return schemas.UserList(
        user_id=user.user_id,
        email=user.email,
        fullname=user.fullname,
        phone_number=user.phone_number,
        state=user.state,
        city=user.city,
        created_on=user.created_on,
        status=user.status,
        verify=user.verify,
    )


def get_current_active_user(
    current_user: schemas.UserList = Depends(get_current_user),
):
    if not current_user.status:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not current_user.verify:
        raise HTTPException(status_code=400, detail="user not verifed!")
    return current_user

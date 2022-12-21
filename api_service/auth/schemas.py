from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    email: str = Field(..., example="sumit@gmail.com")
    password: str = Field(..., example="sumit")
    fullname: str = Field(..., example="sumit kumar")
    phone_number: int = Field(..., example="8540021732")
    state: str = Field(..., example="sumit kumar")
    city: str = Field(..., example="sumit kumar")

    class Config:
        orm_mode = True


class UserList(BaseModel):
    user_id: UUID
    email: Optional[str] = None
    fullname: str
    phone_number: int
    state: str
    city: str
    created_on: Optional[datetime] = None
    status: bool
    verify: bool

    class Config:
        orm_mode = True


class UserPWD(UserList):
    password: str

    class Config:
        orm_mode = True


class PhoneRequest(BaseModel):
    phone_number: int


class ResetPassword(BaseModel):
    new_password: str
    confirm_password: str


class TokenData(BaseModel):
    phone_number: int = None


class ChangePassword(BaseModel):
    old_password: str = Field(..., example="old password")
    new_password: str = Field(..., example="new password")
    confirm_password: str = Field(..., example="confirm password")

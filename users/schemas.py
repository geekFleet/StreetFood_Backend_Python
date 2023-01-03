from typing import Optional
from pydantic import BaseModel


class UpdateUser(BaseModel):
    fullname: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None


class AdminUpdateUser(BaseModel):
    fullname: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    status: Optional[bool] = None

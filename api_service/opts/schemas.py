from pydantic import BaseModel, Field


class CreateOTP(BaseModel):
    phone_number: int


class VerifyOTP(CreateOTP):
    session_id: str
    otp_code: int


class InfoOTP(VerifyOTP):
    otp_failed_count: int
    status: bool

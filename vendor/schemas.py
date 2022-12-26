from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class RequestVendor(BaseModel):
    vendor_name: str = Field(..., example="Hunge&Hpoe")
    location: str = Field(..., example="Patna")
    description: Optional[str] = None
    morning_timing: Optional[str] = None
    evening_timing: Optional[str] = None


class VendorList(BaseModel):
    vendor_id: UUID
    vendor_name: str = Field(..., example="Hunge&Hpoe")
    location: str = Field(..., example="Patna")
    description: Optional[str] = None
    morning_timing: Optional[str] = None
    evening_timing: Optional[str] = None
    created_by: UUID
    last_updated_by: UUID
    created_on: datetime
    status: str


class UpdateVendor(BaseModel):
    vendor_name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    morning_timing: Optional[str] = None
    evening_timing: Optional[str] = None

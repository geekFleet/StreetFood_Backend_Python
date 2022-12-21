from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    BIGINT,
    DateTime,
    Sequence,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.dbUtil import Base
import uuid


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        PG_UUID(as_uuid=True), default=uuid.uuid4, index=True, primary_key=True
    )
    email = Column(String, index=True, nullable=True)
    password = Column(String)
    fullname = Column(String)
    phone_number = Column(BIGINT, unique=True, index=True)
    state = Column(String)
    city = Column(String)
    created_on = Column(DateTime, server_default=func.now())
    status = Column(Boolean, default=True)
    verify = Column(Boolean, default=False)

    vendor = relationship("Vendor", back_populates="user")
    owner = relationship("Review", back_populates="vendor_review")


class Otp(Base):
    __tablename__ = "otps"

    id = Column(Integer, Sequence("otp_id_seq"), primary_key=True)
    phone_number = Column(BIGINT, index=True)
    session_id = Column(String)
    otp_code = Column(Integer)
    status = Column(Boolean, default=True)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now())
    otp_failed_count = Column(Integer, default=0)


class OtpBlock(Base):
    __tablename__ = "otp_blocks"

    id = Column(Integer, Sequence("otp_block_id_seq"), primary_key=True)
    phone_number = Column(BIGINT, index=True)
    created_on = Column(DateTime, server_default=func.now())


class logOutlists(Base):
    __tablename__ = "logoutlists"

    token = Column(String, primary_key=True)
    phone_number = Column(BIGINT, index=True)


class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(
        PG_UUID(as_uuid=True),
        default=uuid.uuid4,
        index=True,
        unique=True,
        primary_key=True,
    )
    vendor_name = Column(String)
    location = Column(String)
    description = Column(String, nullable=True)
    morning_timing = Column(String, nullable=True)
    evening_timing = Column(String, nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    last_updated_on = Column(DateTime, server_default=func.now())
    created_on = Column(DateTime, server_default=func.now())
    status = Column(Boolean, default=True)

    user = relationship("User", back_populates="vendor")
    review = relationship("Review", back_populates="vendors")


class Review(Base):
    __tablename__ = "vendor_review"

    id = Column(Integer, Sequence("vendor_review_id_seq"), primary_key=True)
    vendor_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("vendors.vendor_id"), index=True
    )
    taste = Column(Float, nullable=True)
    price_to_quality = Column(Float, nullable=True)
    hygiene = Column(Float, nullable=True)
    service = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    overall_rating = Column(Float, nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    last_updated_on = Column(DateTime, server_default=func.now())
    created_on = Column(DateTime, server_default=func.now())
    status = Column(Boolean, default=True)

    vendor_review = relationship("User", back_populates="owner")
    vendors = relationship("Vendor", back_populates="review")

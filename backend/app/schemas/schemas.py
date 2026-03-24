"""
Pydantic schemas for request/response validation
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# Auth schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime


# Job schemas
class JobCreate(BaseModel):
    filename: str
    mime_type: str
    file_size: int
    complexity: str = "auto"  # auto, simple, complex


class JobResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    status: str
    complexity: str
    mime_type: str
    file_size: int
    original_url: Optional[str] = None
    output_dst_url: Optional[str] = None
    output_svg_url: Optional[str] = None
    output_json_url: Optional[str] = None
    price: float
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class JobStatus(BaseModel):
    id: str
    status: str
    progress: int = 0
    message: Optional[str] = None
    output_urls: Optional[dict] = None


# Payment schemas
class PaymentRequest(BaseModel):
    job_id: str
    phone: str = Field(..., pattern=r"^254[0-9]{9}$")


class PaymentCallback(BaseModel):
    transaction_type: str
    trans_id: str
    trans_time: str
    trans_amount: float
    business_shortcode: str
    bill_ref: str
    invoice_number: str
    account_number: str
    third_party_trans_id: Optional[str] = None
    msisdn: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None


class PaymentStatus(BaseModel):
    job_id: str
    status: str
    transaction_id: Optional[str] = None
    amount: float
    phone: str
    created_at: datetime


# Wallet schemas
class WalletTopup(BaseModel):
    amount: float = Field(..., gt=0)
    phone: str = Field(..., pattern=r"^254[0-9]{9}$")


class WalletBalance(BaseModel):
    user_id: str
    balance: float
    currency: str = "KES"


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    type: str
    status: str
    description: Optional[str] = None
    reference: Optional[str] = None
    created_at: datetime


# Upload schema
class UploadResponse(BaseModel):
    upload_url: str
    fields: dict
    job_id: str


# Error response
class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None

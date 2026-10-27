from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field

class MembershipPlanOut(BaseModel):
    id: int
    name: str
    duration_type: str
    duration_days: int
    price: float
    description: str
    features: List[str]
    is_active: bool
    created_at: datetime

class MembershipPlanCreate(BaseModel):
    name: str
    duration_type: str = "monthly"
    duration_days: int = 30
    price: float
    description: Optional[str] = ""
    features: Optional[List[str]] = []

class MembershipPlanUpdate(BaseModel):
    name: Optional[str] = None
    duration_type: Optional[str] = None
    duration_days: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    is_active: Optional[bool] = None

class SubscriptionOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    member_email: str
    member_phone: str
    plan_id: int
    plan_name: str
    plan_price: float
    start_date: date
    end_date: date
    status: str
    notes: str
    days_left: int
    payment_status: Optional[str] = "pending_verification"
    utr_number: Optional[str] = ""
    is_verified: bool = False
    created_at: datetime

class SubscriptionCreate(BaseModel):
    member_id: int
    plan_id: int
    start_date: Optional[date] = None
    notes: Optional[str] = ""

class SubscriptionRenew(BaseModel):
    plan_id: int
    payment_method: str = "upi"
    amount: Optional[float] = None
    utr_number: Optional[str] = ""
    notes: Optional[str] = ""

class PaymentOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    member_email: str
    member_phone: Optional[str] = ""
    subscription_id: Optional[int] = None
    plan_id: Optional[int] = None
    plan_name: Optional[str] = None
    amount: float
    payment_method: str
    payment_type: str
    status: str
    invoice_number: str
    utr_number: Optional[str] = ""
    upi_vpa: Optional[str] = ""
    rejection_reason: Optional[str] = ""
    verified_at: Optional[datetime] = None
    transaction_date: datetime
    notes: str

class PaymentCreate(BaseModel):
    member_id: int
    subscription_id: Optional[int] = None
    amount: float
    payment_method: str = "upi"
    payment_type: str = "initial"
    status: str = "completed"
    utr_number: Optional[str] = ""
    notes: Optional[str] = ""

class SubmitUTRRequest(BaseModel):
    plan_id: int
    utr_number: str = Field(min_length=6, max_length=50)
    upi_vpa: Optional[str] = "setfit@upi"
    notes: Optional[str] = ""

class VerifyPaymentRequest(BaseModel):
    notes: Optional[str] = "Bank confirmed & verified by admin"

class RejectPaymentRequest(BaseModel):
    reason: str = Field(min_length=3)

class MemberOnboardSchema(BaseModel):
    # Member Personal Info
    first_name: str
    last_name: Optional[str] = ""
    email: EmailStr
    phone: str
    password: Optional[str] = "GymMember@2026"
    branch_id: Optional[int] = None
    
    # Subscription & Plan
    plan_id: int
    start_date: Optional[date] = None
    
    # Payment details
    payment_method: str = "card"
    amount_paid: Optional[float] = None
    utr_number: Optional[str] = ""
    payment_notes: Optional[str] = "Initial registration payment"

class EnquiryCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: str
    fitness_goal: Optional[str] = "General Fitness"
    preferred_time: Optional[str] = "Morning (6 AM - 10 AM)"
    message: Optional[str] = ""

class EnquiryOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    fitness_goal: str
    preferred_time: str
    message: str
    status: str
    notes: str
    created_at: datetime

class EnquiryStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = ""

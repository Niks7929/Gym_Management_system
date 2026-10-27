from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: str
    role: str
    branch_id: Optional[int] = None
    branch_name: Optional[str] = None
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserOut

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str
    last_name: Optional[str] = ""
    phone: Optional[str] = ""
    role: str = "member"
    branch_id: Optional[int] = None

class MemberRegisterRequest(BaseModel):
    first_name: str
    last_name: Optional[str] = ""
    email: EmailStr
    phone: str
    password: str = Field(min_length=6)
    role: Optional[str] = "member"
    plan_id: Optional[int] = None
    branch_id: Optional[int] = None
    fitness_goal: Optional[str] = ""
    specialization: Optional[str] = ""
    experience_years: Optional[str] = ""
    certifications: Optional[str] = ""
    shift_preference: Optional[str] = ""

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    branch_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)

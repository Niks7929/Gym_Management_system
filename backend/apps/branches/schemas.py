from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class BranchOut(BaseModel):
    id: int
    name: str
    code: str
    address: str
    city: str
    phone: str
    email: str
    is_active: bool
    created_at: datetime

class BranchCreate(BaseModel):
    name: str
    code: str
    address: str
    city: str
    phone: str
    email: Optional[EmailStr] = None

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class GymSettingOut(BaseModel):
    gym_name: str
    tagline: str
    announcement_bar: str
    hero_headline: str
    hero_subtitle: str
    hero_badge_text: str
    hero_cta_primary: str
    hero_cta_secondary: str
    theme_accent: str
    stat_access_hours: str
    stat_equipment_text: str
    stat_trainers_count: str
    stat_members_count: str
    contact_email: str
    contact_phone: str
    address: str
    currency_symbol: str
    date_format: str
    tax_percentage: float
    updated_at: datetime

class GymSettingUpdate(BaseModel):
    gym_name: Optional[str] = None
    tagline: Optional[str] = None
    announcement_bar: Optional[str] = None
    hero_headline: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_badge_text: Optional[str] = None
    hero_cta_primary: Optional[str] = None
    hero_cta_secondary: Optional[str] = None
    theme_accent: Optional[str] = None
    stat_access_hours: Optional[str] = None
    stat_equipment_text: Optional[str] = None
    stat_trainers_count: Optional[str] = None
    stat_members_count: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    currency_symbol: Optional[str] = None
    date_format: Optional[str] = None
    tax_percentage: Optional[float] = None

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from pydantic import BaseModel

class RevenueMonthPoint(BaseModel):
    month: str
    revenue: float
    transactions_count: int

class PlanDistributionPoint(BaseModel):
    plan_name: str
    member_count: int
    percentage: float

class AdminDashboardStatsOut(BaseModel):
    total_members: int
    active_members: int
    expired_members: int
    total_trainers: int
    total_receptionists: int
    today_revenue: float
    month_revenue: float
    total_revenue: float
    today_checkins: int
    monthly_revenue_trend: List[RevenueMonthPoint]
    plan_distribution: List[PlanDistributionPoint]

class ReceptionistDashboardStatsOut(BaseModel):
    total_members: int
    active_members: int
    expiring_soon_7days: int
    today_checkins: int
    today_revenue: float

class TrainerDashboardStatsOut(BaseModel):
    assigned_clients_count: int
    active_workouts_count: int
    active_diets_count: int
    today_client_checkins: int

class MemberDashboardStatsOut(BaseModel):
    has_active_subscription: bool
    plan_name: Optional[str] = None
    days_left: int
    expiry_date: Optional[date] = None
    total_checkins_this_month: int
    active_workout_title: Optional[str] = None
    active_diet_title: Optional[str] = None
    daily_calories: Optional[int] = None

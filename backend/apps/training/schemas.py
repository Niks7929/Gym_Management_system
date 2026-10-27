from typing import List, Dict, Any, Optional
from datetime import date, datetime
from pydantic import BaseModel

class WorkoutPlanOut(BaseModel):
    id: int
    trainer_id: Optional[int] = None
    trainer_name: Optional[str] = None
    member_id: int
    member_name: str
    title: str
    goal: str
    exercises_schedule: List[Any]
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    created_at: datetime

class WorkoutPlanCreate(BaseModel):
    member_id: int
    title: str
    goal: Optional[str] = "Strength & Conditioning"
    exercises_schedule: List[Any]
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class WorkoutPlanUpdate(BaseModel):
    title: Optional[str] = None
    goal: Optional[str] = None
    exercises_schedule: Optional[List[Any]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None

class DietPlanOut(BaseModel):
    id: int
    trainer_id: Optional[int] = None
    trainer_name: Optional[str] = None
    member_id: int
    member_name: str
    title: str
    daily_calories: int
    macros: Dict[str, Any]
    meals_schedule: List[Any]
    guidelines: str
    is_active: bool
    created_at: datetime

class DietPlanCreate(BaseModel):
    member_id: int
    title: str
    daily_calories: int = 2200
    macros: Optional[Dict[str, Any]] = None
    meals_schedule: List[Any]
    guidelines: Optional[str] = ""

class DietPlanUpdate(BaseModel):
    title: Optional[str] = None
    daily_calories: Optional[int] = None
    macros: Optional[Dict[str, Any]] = None
    meals_schedule: Optional[List[Any]] = None
    guidelines: Optional[str] = None
    is_active: Optional[bool] = None

class TrainerClientOut(BaseModel):
    id: int
    trainer_id: int
    trainer_name: str
    member_id: int
    member_name: str
    member_email: str
    member_phone: str
    start_date: date
    is_active: bool
    notes: str
    active_plan_name: Optional[str] = None
    days_left_in_membership: Optional[int] = None

class TrainerClientAssignCreate(BaseModel):
    trainer_id: int
    member_id: int
    notes: Optional[str] = ""

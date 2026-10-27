from typing import Optional
from datetime import date, time, datetime
from pydantic import BaseModel

class AttendanceOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    member_email: str
    member_phone: str
    date: date
    check_in_time: time
    check_out_time: Optional[time] = None
    status: str
    notes: str
    logged_by_name: Optional[str] = None
    created_at: datetime

class AttendanceCheckInSchema(BaseModel):
    member_id: int
    date: Optional[date] = None
    check_in_time: Optional[time] = None
    status: Optional[str] = "present"
    notes: Optional[str] = ""

class AttendanceCheckOutSchema(BaseModel):
    attendance_id: int
    check_out_time: Optional[time] = None

class DailyAttendanceSummary(BaseModel):
    date: date
    total_checkins: int
    present_count: int
    late_count: int

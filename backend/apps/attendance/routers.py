from typing import List, Optional
from datetime import date
from django.db.models import Q
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from .models import Attendance, AttendanceStatus
from .schemas import AttendanceOut, AttendanceCheckInSchema, AttendanceCheckOutSchema, DailyAttendanceSummary
from apps.accounts.auth import jwt_auth, require_roles
from apps.accounts.models import UserRole

User = get_user_model()
router = Router(tags=["Attendance Logging"])

def map_attendance_to_out(att: Attendance) -> AttendanceOut:
    return AttendanceOut(
        id=att.id,
        member_id=att.member_id,
        member_name=att.member.full_name,
        member_email=att.member.email,
        member_phone=att.member.phone,
        date=att.date,
        check_in_time=att.check_in_time,
        check_out_time=att.check_out_time,
        status=att.status,
        notes=att.notes,
        logged_by_name=att.logged_by.full_name if att.logged_by else None,
        created_at=att.created_at
    )

@router.get("/attendances", response=List[AttendanceOut], auth=jwt_auth)
def list_attendance(
    request,
    date_filter: Optional[date] = None,
    member_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    current_user = request.auth
    qs = Attendance.objects.select_related('member', 'logged_by').all()

    if current_user.role == UserRole.MEMBER:
        qs = qs.filter(member=current_user)
    elif member_id:
        qs = qs.filter(member_id=member_id)

    if date_filter:
        qs = qs.filter(date=date_filter)
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(
            Q(member__first_name__icontains=search) |
            Q(member__last_name__icontains=search) |
            Q(member__email__icontains=search) |
            Q(member__phone__icontains=search)
        )

    return [map_attendance_to_out(a) for a in qs.order_by('-date', '-check_in_time')]

@router.post("/attendances/check-in", response={201: AttendanceOut}, auth=jwt_auth)
def check_in(request, payload: AttendanceCheckInSchema):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.TRAINER)(request.auth)
    
    member = User.objects.filter(id=payload.member_id).first()
    if not member:
        raise HttpError(404, "Member not found")

    today = payload.date or timezone.now().date()
    now_time = payload.check_in_time or timezone.now().time()

    att = Attendance.objects.filter(member=member, date=today).first()
    if att:
        raise HttpError(400, f"{member.full_name} has already checked in today at {att.check_in_time.strftime('%H:%M')}")

    att = Attendance.objects.create(
        member=member,
        date=today,
        check_in_time=now_time,
        status=payload.status or AttendanceStatus.PRESENT,
        notes=payload.notes or "",
        logged_by=request.auth
    )
    return 201, map_attendance_to_out(att)

@router.post("/attendances/check-out", response=AttendanceOut, auth=jwt_auth)
def check_out(request, payload: AttendanceCheckOutSchema):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.TRAINER)(request.auth)
    
    att = Attendance.objects.filter(id=payload.attendance_id).first()
    if not att:
        raise HttpError(404, "Attendance record not found")

    att.check_out_time = payload.check_out_time or timezone.now().time()
    att.save()
    return map_attendance_to_out(att)

@router.get("/attendances/today-summary", response=DailyAttendanceSummary, auth=jwt_auth)
def today_attendance_summary(request):
    today = timezone.now().date()
    qs = Attendance.objects.filter(date=today)
    return DailyAttendanceSummary(
        date=today,
        total_checkins=qs.count(),
        present_count=qs.filter(status=AttendanceStatus.PRESENT).count(),
        late_count=qs.filter(status=AttendanceStatus.LATE).count()
    )

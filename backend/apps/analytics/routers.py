from typing import List
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from .schemas import (
    AdminDashboardStatsOut, ReceptionistDashboardStatsOut,
    TrainerDashboardStatsOut, MemberDashboardStatsOut,
    RevenueMonthPoint, PlanDistributionPoint
)
from apps.accounts.auth import jwt_auth, require_roles
from apps.accounts.models import UserRole
from apps.memberships.models import Subscription, SubscriptionStatus, Payment, PaymentStatus, MembershipPlan
from apps.attendance.models import Attendance, AttendanceStatus
from apps.training.models import TrainerClientAssignment, WorkoutPlan, DietPlan

User = get_user_model()
router = Router(tags=["Analytics & Dashboard Stats"])

@router.get("/admin", response=AdminDashboardStatsOut, auth=jwt_auth)
def get_admin_dashboard_stats(request):
    require_roles(UserRole.ADMIN)(request.auth)
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_members = User.objects.filter(role=UserRole.MEMBER).count()
    active_members = Subscription.objects.filter(status=SubscriptionStatus.ACTIVE).count()
    expired_members = Subscription.objects.filter(status=SubscriptionStatus.EXPIRED).count()
    total_trainers = User.objects.filter(role=UserRole.TRAINER, is_active=True).count()
    total_receptionists = User.objects.filter(role=UserRole.RECEPTIONIST, is_active=True).count()

    today_revenue = Payment.objects.filter(
        status=PaymentStatus.COMPLETED,
        transaction_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0.0

    month_revenue = Payment.objects.filter(
        status=PaymentStatus.COMPLETED,
        transaction_date__date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0.0

    total_revenue = Payment.objects.filter(
        status=PaymentStatus.COMPLETED
    ).aggregate(total=Sum('amount'))['total'] or 0.0

    today_checkins = Attendance.objects.filter(date=today).count()

    # 6-Month Monthly Revenue Trend
    monthly_trend: List[RevenueMonthPoint] = []
    for i in range(5, -1, -1):
        # Approximate 30 days buckets
        bucket_date = today - timedelta(days=i * 30)
        month_label = bucket_date.strftime("%b %Y")
        start_of_bucket = bucket_date.replace(day=1)
        # End of bucket
        if start_of_bucket.month == 12:
            end_of_bucket = start_of_bucket.replace(year=start_of_bucket.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_bucket = start_of_bucket.replace(month=start_of_bucket.month + 1, day=1) - timedelta(days=1)

        rev_aggr = Payment.objects.filter(
            status=PaymentStatus.COMPLETED,
            transaction_date__date__gte=start_of_bucket,
            transaction_date__date__lte=end_of_bucket
        ).aggregate(total=Sum('amount'), count=Count('id'))

        monthly_trend.append(RevenueMonthPoint(
            month=month_label,
            revenue=float(rev_aggr['total'] or 0.0),
            transactions_count=rev_aggr['count'] or 0
        ))

    # Plan distribution
    plan_dist: List[PlanDistributionPoint] = []
    total_subs = max(1, Subscription.objects.count())
    for plan in MembershipPlan.objects.all():
        count = Subscription.objects.filter(plan=plan).count()
        if count > 0:
            plan_dist.append(PlanDistributionPoint(
                plan_name=plan.name,
                member_count=count,
                percentage=round((count / total_subs) * 100, 1)
            ))

    return AdminDashboardStatsOut(
        total_members=total_members,
        active_members=active_members,
        expired_members=expired_members,
        total_trainers=total_trainers,
        total_receptionists=total_receptionists,
        today_revenue=float(today_revenue),
        month_revenue=float(month_revenue),
        total_revenue=float(total_revenue),
        today_checkins=today_checkins,
        monthly_revenue_trend=monthly_trend,
        plan_distribution=plan_dist
    )

@router.get("/receptionist", response=ReceptionistDashboardStatsOut, auth=jwt_auth)
def get_receptionist_dashboard_stats(request):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)(request.auth)
    today = timezone.now().date()
    cutoff_7days = today + timedelta(days=7)

    total_members = User.objects.filter(role=UserRole.MEMBER).count()
    active_members = Subscription.objects.filter(status=SubscriptionStatus.ACTIVE).count()
    expiring_soon = Subscription.objects.filter(
        status=SubscriptionStatus.ACTIVE,
        end_date__gte=today,
        end_date__lte=cutoff_7days
    ).count()

    today_checkins = Attendance.objects.filter(date=today).count()
    today_revenue = Payment.objects.filter(
        status=PaymentStatus.COMPLETED,
        transaction_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0.0

    return ReceptionistDashboardStatsOut(
        total_members=total_members,
        active_members=active_members,
        expiring_soon_7days=expiring_soon,
        today_checkins=today_checkins,
        today_revenue=float(today_revenue)
    )

@router.get("/trainer", response=TrainerDashboardStatsOut, auth=jwt_auth)
def get_trainer_dashboard_stats(request):
    require_roles(UserRole.ADMIN, UserRole.TRAINER)(request.auth)
    trainer = request.auth
    today = timezone.now().date()

    assigned_clients = TrainerClientAssignment.objects.filter(trainer=trainer, is_active=True).values_list('member_id', flat=True)
    assigned_count = len(assigned_clients)

    active_workouts = WorkoutPlan.objects.filter(trainer=trainer, is_active=True).count()
    active_diets = DietPlan.objects.filter(trainer=trainer, is_active=True).count()

    today_client_checkins = Attendance.objects.filter(
        member_id__in=assigned_clients,
        date=today
    ).count()

    return TrainerDashboardStatsOut(
        assigned_clients_count=assigned_count,
        active_workouts_count=active_workouts,
        active_diets_count=active_diets,
        today_client_checkins=today_client_checkins
    )

@router.get("/member", response=MemberDashboardStatsOut, auth=jwt_auth)
def get_member_dashboard_stats(request):
    member = request.auth
    today = timezone.now().date()
    month_start = today.replace(day=1)

    sub = Subscription.objects.select_related('plan').filter(
        member=member,
        status=SubscriptionStatus.ACTIVE
    ).first()

    days_left = max(0, (sub.end_date - today).days) if sub else 0
    total_checkins_this_month = Attendance.objects.filter(
        member=member,
        date__gte=month_start
    ).count()

    workout = WorkoutPlan.objects.filter(member=member, is_active=True).order_by('-created_at').first()
    diet = DietPlan.objects.filter(member=member, is_active=True).order_by('-created_at').first()

    return MemberDashboardStatsOut(
        has_active_subscription=sub is not None,
        plan_name=sub.plan.name if sub else None,
        days_left=days_left,
        expiry_date=sub.end_date if sub else None,
        total_checkins_this_month=total_checkins_this_month,
        active_workout_title=workout.title if workout else "No routine assigned yet",
        active_diet_title=diet.title if diet else "No meal plan assigned yet",
        daily_calories=diet.daily_calories if diet else None
    )

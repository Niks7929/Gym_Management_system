from typing import List, Optional
from datetime import date
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from .models import TrainerClientAssignment, WorkoutPlan, DietPlan
from .schemas import (
    WorkoutPlanOut, WorkoutPlanCreate, WorkoutPlanUpdate,
    DietPlanOut, DietPlanCreate, DietPlanUpdate,
    TrainerClientOut, TrainerClientAssignCreate
)
from apps.accounts.auth import jwt_auth, require_roles
from apps.accounts.models import UserRole
from apps.memberships.models import Subscription, SubscriptionStatus

User = get_user_model()
router = Router(tags=["Training, Workouts & Diets"])

def map_workout_to_out(w: WorkoutPlan) -> WorkoutPlanOut:
    return WorkoutPlanOut(
        id=w.id,
        trainer_id=w.trainer_id,
        trainer_name=w.trainer.full_name if w.trainer else "Gym Master Coach",
        member_id=w.member_id,
        member_name=w.member.full_name,
        title=w.title,
        goal=w.goal,
        exercises_schedule=w.exercises_schedule if isinstance(w.exercises_schedule, list) else [],
        start_date=w.start_date,
        end_date=w.end_date,
        is_active=w.is_active,
        created_at=w.created_at
    )

def map_diet_to_out(d: DietPlan) -> DietPlanOut:
    return DietPlanOut(
        id=d.id,
        trainer_id=d.trainer_id,
        trainer_name=d.trainer.full_name if d.trainer else "Gym Nutrition Coach",
        member_id=d.member_id,
        member_name=d.member.full_name,
        title=d.title,
        daily_calories=d.daily_calories,
        macros=d.macros if isinstance(d.macros, dict) else {},
        meals_schedule=d.meals_schedule if isinstance(d.meals_schedule, list) else [],
        guidelines=d.guidelines,
        is_active=d.is_active,
        created_at=d.created_at
    )

# --- Trainer Clients ---
@router.get("/clients", response=List[TrainerClientOut], auth=jwt_auth)
def list_trainer_clients(request, trainer_id: Optional[int] = None):
    current_user = request.auth
    qs = TrainerClientAssignment.objects.select_related('trainer', 'member').all()

    if current_user.role == UserRole.TRAINER:
        qs = qs.filter(trainer=current_user)
    elif trainer_id:
        qs = qs.filter(trainer_id=trainer_id)

    results = []
    today = timezone.now().date()
    for item in qs:
        active_sub = Subscription.objects.filter(member=item.member, status=SubscriptionStatus.ACTIVE).first()
        days_left = max(0, (active_sub.end_date - today).days) if active_sub else 0
        plan_name = active_sub.plan.name if active_sub else "No Active Plan"

        results.append(TrainerClientOut(
            id=item.id,
            trainer_id=item.trainer_id,
            trainer_name=item.trainer.full_name,
            member_id=item.member_id,
            member_name=item.member.full_name,
            member_email=item.member.email,
            member_phone=item.member.phone,
            start_date=item.start_date,
            is_active=item.is_active,
            notes=item.notes,
            active_plan_name=plan_name,
            days_left_in_membership=days_left
        ))
    return results

@router.post("/clients/assign", response={201: dict}, auth=jwt_auth)
def assign_client(request, payload: TrainerClientAssignCreate):
    require_roles(UserRole.ADMIN, UserRole.TRAINER)(request.auth)
    trainer = User.objects.filter(id=payload.trainer_id, role=UserRole.TRAINER).first()
    if not trainer:
        raise HttpError(404, "Trainer not found")
        
    member = User.objects.filter(id=payload.member_id, role=UserRole.MEMBER).first()
    if not member:
        raise HttpError(404, "Member not found")

    assignment, created = TrainerClientAssignment.objects.get_or_create(
        trainer=trainer,
        member=member,
        defaults={'notes': payload.notes or "", 'is_active': True}
    )
    if not created:
        assignment.is_active = True
        if payload.notes:
            assignment.notes = payload.notes
        assignment.save()

    return 201, {"message": f"Client {member.full_name} assigned to Trainer {trainer.full_name}"}

# --- Workout Plans ---
@router.get("/workouts", response=List[WorkoutPlanOut], auth=jwt_auth)
def list_workouts(request, member_id: Optional[int] = None):
    current_user = request.auth
    qs = WorkoutPlan.objects.select_related('trainer', 'member').all()

    if current_user.role == UserRole.MEMBER:
        qs = qs.filter(member=current_user)
    elif current_user.role == UserRole.TRAINER:
        qs = qs.filter(trainer=current_user)
    elif member_id:
        qs = qs.filter(member_id=member_id)

    return [map_workout_to_out(w) for w in qs]

@router.get("/workouts/my-active", response=Optional[WorkoutPlanOut], auth=jwt_auth)
def get_my_active_workout(request):
    current_user = request.auth
    workout = WorkoutPlan.objects.select_related('trainer', 'member').filter(
        member=current_user,
        is_active=True
    ).order_by('-created_at').first()
    if not workout:
        return None
    return map_workout_to_out(workout)

@router.post("/workouts", response={201: WorkoutPlanOut}, auth=jwt_auth)
def create_workout_plan(request, payload: WorkoutPlanCreate):
    require_roles(UserRole.ADMIN, UserRole.TRAINER)(request.auth)
    member = User.objects.filter(id=payload.member_id).first()
    if not member:
        raise HttpError(404, "Member not found")

    workout = WorkoutPlan.objects.create(
        trainer=request.auth if request.auth.role == UserRole.TRAINER else None,
        member=member,
        title=payload.title,
        goal=payload.goal or "Strength & Conditioning",
        exercises_schedule=payload.exercises_schedule,
        start_date=payload.start_date or timezone.now().date(),
        end_date=payload.end_date,
        is_active=True
    )
    return 201, map_workout_to_out(workout)

@router.put("/workouts/{workout_id}", response=WorkoutPlanOut, auth=jwt_auth)
def update_workout_plan(request, workout_id: int, payload: WorkoutPlanUpdate):
    require_roles(UserRole.ADMIN, UserRole.TRAINER)(request.auth)
    workout = WorkoutPlan.objects.filter(id=workout_id).first()
    if not workout:
        raise HttpError(404, "Workout plan not found")

    if payload.title is not None:
        workout.title = payload.title
    if payload.goal is not None:
        workout.goal = payload.goal
    if payload.exercises_schedule is not None:
        workout.exercises_schedule = payload.exercises_schedule
    if payload.start_date is not None:
        workout.start_date = payload.start_date
    if payload.end_date is not None:
        workout.end_date = payload.end_date
    if payload.is_active is not None:
        workout.is_active = payload.is_active

    workout.save()
    return map_workout_to_out(workout)

# --- Diet Plans ---
@router.get("/diets", response=List[DietPlanOut], auth=jwt_auth)
def list_diets(request, member_id: Optional[int] = None):
    current_user = request.auth
    qs = DietPlan.objects.select_related('trainer', 'member').all()

    if current_user.role == UserRole.MEMBER:
        qs = qs.filter(member=current_user)
    elif current_user.role == UserRole.TRAINER:
        qs = qs.filter(trainer=current_user)
    elif member_id:
        qs = qs.filter(member_id=member_id)

    return [map_diet_to_out(d) for d in qs]

@router.get("/diets/my-active", response=Optional[DietPlanOut], auth=jwt_auth)
def get_my_active_diet(request):
    current_user = request.auth
    diet = DietPlan.objects.select_related('trainer', 'member').filter(
        member=current_user,
        is_active=True
    ).order_by('-created_at').first()
    if not diet:
        return None
    return map_diet_to_out(diet)

@router.post("/diets", response={201: DietPlanOut}, auth=jwt_auth)
def create_diet_plan(request, payload: DietPlanCreate):
    require_roles(UserRole.ADMIN, UserRole.TRAINER)(request.auth)
    member = User.objects.filter(id=payload.member_id).first()
    if not member:
        raise HttpError(404, "Member not found")

    diet = DietPlan.objects.create(
        trainer=request.auth if request.auth.role == UserRole.TRAINER else None,
        member=member,
        title=payload.title,
        daily_calories=payload.daily_calories,
        macros=payload.macros or {"protein": "150g", "carbs": "200g", "fats": "55g"},
        meals_schedule=payload.meals_schedule,
        guidelines=payload.guidelines or "",
        is_active=True
    )
    return 201, map_diet_to_out(diet)

@router.put("/diets/{diet_id}", response=DietPlanOut, auth=jwt_auth)
def update_diet_plan(request, diet_id: int, payload: DietPlanUpdate):
    require_roles(UserRole.ADMIN, UserRole.TRAINER)(request.auth)
    diet = DietPlan.objects.filter(id=diet_id).first()
    if not diet:
        raise HttpError(404, "Diet plan not found")

    if payload.title is not None:
        diet.title = payload.title
    if payload.daily_calories is not None:
        diet.daily_calories = payload.daily_calories
    if payload.macros is not None:
        diet.macros = payload.macros
    if payload.meals_schedule is not None:
        diet.meals_schedule = payload.meals_schedule
    if payload.guidelines is not None:
        diet.guidelines = payload.guidelines
    if payload.is_active is not None:
        diet.is_active = payload.is_active

    diet.save()
    return map_diet_to_out(diet)

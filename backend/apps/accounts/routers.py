from typing import List, Optional
from datetime import timedelta
from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import UserRole
from .schemas import (
    LoginRequest, TokenResponse, UserOut, UserCreate, UserUpdate,
    ChangePasswordSchema, MemberRegisterRequest
)
from .auth import jwt_auth, create_jwt_token, require_roles
from apps.branches.models import Branch
from apps.memberships.models import MembershipPlan, Subscription, Payment, SubscriptionStatus, PaymentType, PaymentStatus

User = get_user_model()
router = Router(tags=["Authentication & Users"])

def map_user_to_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role,
        branch_id=user.branch_id,
        branch_name=user.branch.name if user.branch else None,
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.post("/login", response=TokenResponse, auth=None)
def login(request, payload: LoginRequest):
    user = User.objects.filter(email=payload.email).first()
    if not user or not user.check_password(payload.password):
        raise HttpError(401, "Invalid email or password")
    
    if not user.is_active:
        raise HttpError(403, "This account has been deactivated. Please contact your admin.")
    
    token = create_jwt_token(user)
    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        user=map_user_to_out(user)
    )

@router.post("/register", response={201: TokenResponse}, auth=None)
def register(request, payload: MemberRegisterRequest):
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "A user with this email already exists")

    branch = None
    if payload.branch_id:
        branch = Branch.objects.filter(id=payload.branch_id).first()
    if not branch:
        branch = Branch.objects.first()

    requested_role = payload.role.lower() if payload.role else "member"
    if requested_role not in [UserRole.MEMBER, UserRole.TRAINER, UserRole.RECEPTIONIST]:
        requested_role = UserRole.MEMBER

    with transaction.atomic():
        user = User.objects.create_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name or "",
            phone=payload.phone,
            role=requested_role,
            branch=branch
        )

        # For athlete members with selected plan, create pending subscription awaiting UPI confirmation
        if requested_role == UserRole.MEMBER and payload.plan_id:
            plan = MembershipPlan.objects.filter(id=payload.plan_id).first()
            if plan:
                today = timezone.now().date()
                sub = Subscription.objects.create(
                    member=user,
                    plan=plan,
                    start_date=today,
                    end_date=today + timedelta(days=plan.duration_days),
                    status=SubscriptionStatus.PENDING_VERIFICATION,
                    notes=f"Online athlete registration: {payload.fitness_goal or 'General Fitness'}"
                )
                Payment.objects.create(
                    member=user,
                    subscription=sub,
                    amount=plan.price,
                    payment_method="upi",
                    payment_type=PaymentType.INITIAL,
                    status=PaymentStatus.PENDING_VERIFICATION,
                    notes=f"Pending UPI UTR verification - {plan.name}"
                )

    token = create_jwt_token(user)
    return 201, TokenResponse(
        access_token=token,
        token_type="Bearer",
        user=map_user_to_out(user)
    )

@router.get("/me", response=UserOut, auth=jwt_auth)
def get_current_user(request):
    return map_user_to_out(request.auth)

@router.post("/change-password", response={200: dict}, auth=jwt_auth)
def change_password(request, payload: ChangePasswordSchema):
    user = request.auth
    if not user.check_password(payload.current_password):
        raise HttpError(400, "Incorrect current password")
    user.set_password(payload.new_password)
    user.save()
    return 200, {"message": "Password updated successfully"}

@router.get("/users", response=List[UserOut], auth=jwt_auth)
def list_users(
    request,
    role: Optional[str] = None,
    branch_id: Optional[int] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None
):
    current_user = request.auth
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.TRAINER)(current_user)
    
    qs = User.objects.select_related('branch').all()
    
    if role:
        qs = qs.filter(role=role)
    if branch_id:
        qs = qs.filter(branch_id=branch_id)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    return [map_user_to_out(u) for u in qs.order_by('-id')]

@router.post("/users", response={201: UserOut}, auth=jwt_auth)
def create_user(request, payload: UserCreate):
    current_user = request.auth
    
    if current_user.role == UserRole.RECEPTIONIST and payload.role != UserRole.MEMBER:
        raise HttpError(403, "Receptionists can only register members")
    elif current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
        raise HttpError(403, "Permission denied")

    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "A user with this email already exists")

    branch = None
    if payload.branch_id:
        branch = Branch.objects.filter(id=payload.branch_id).first()
    elif current_user.branch:
        branch = current_user.branch

    user = User.objects.create_user(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name or "",
        phone=payload.phone or "",
        role=payload.role,
        branch=branch
    )
    return 201, map_user_to_out(user)

@router.get("/users/{user_id}", response=UserOut, auth=jwt_auth)
def get_user_detail(request, user_id: int):
    current_user = request.auth
    if current_user.role == UserRole.MEMBER and current_user.id != user_id:
        raise HttpError(403, "Permission denied")
        
    user = User.objects.select_related('branch').filter(id=user_id).first()
    if not user:
        raise HttpError(404, "User not found")
    return map_user_to_out(user)

@router.put("/users/{user_id}", response=UserOut, auth=jwt_auth)
def update_user(request, user_id: int, payload: UserUpdate):
    current_user = request.auth
    if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST] and current_user.id != user_id:
        raise HttpError(403, "Permission denied")
        
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise HttpError(404, "User not found")

    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.branch_id is not None and current_user.role == UserRole.ADMIN:
        user.branch_id = payload.branch_id
    if payload.is_active is not None and current_user.role == UserRole.ADMIN:
        user.is_active = payload.is_active
    if payload.role is not None and current_user.role == UserRole.ADMIN:
        user.role = payload.role
    if payload.password:
        user.set_password(payload.password)
        
    user.save()
    return map_user_to_out(user)

@router.delete("/users/{user_id}", response={200: dict}, auth=jwt_auth)
def delete_user(request, user_id: int):
    current_user = request.auth
    require_roles(UserRole.ADMIN)(current_user)
    
    if current_user.id == user_id:
        raise HttpError(400, "Cannot delete your own admin account")
        
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise HttpError(404, "User not found")
    
    user.is_active = False
    user.save()
    return 200, {"message": f"User {user.email} deactivated successfully"}

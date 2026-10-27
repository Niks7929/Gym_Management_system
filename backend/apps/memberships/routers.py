from typing import List, Optional
from datetime import date, timedelta
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from .models import (
    MembershipPlan, Subscription, Payment, SubscriptionStatus,
    PaymentStatus, PaymentType, PaymentMethod, Enquiry, EnquiryStatus
)
from .schemas import (
    MembershipPlanOut, MembershipPlanCreate, MembershipPlanUpdate,
    SubscriptionOut, SubscriptionCreate, SubscriptionRenew,
    PaymentOut, PaymentCreate, MemberOnboardSchema,
    SubmitUTRRequest, VerifyPaymentRequest, RejectPaymentRequest,
    EnquiryCreate, EnquiryOut, EnquiryStatusUpdate
)
from apps.accounts.auth import jwt_auth, require_roles
from apps.accounts.models import UserRole
from apps.branches.models import Branch

User = get_user_model()
router = Router(tags=["Memberships, Subscriptions & Payments"])

def map_plan_to_out(plan: MembershipPlan) -> MembershipPlanOut:
    return MembershipPlanOut(
        id=plan.id,
        name=plan.name,
        duration_type=plan.duration_type,
        duration_days=plan.duration_days,
        price=float(plan.price),
        description=plan.description,
        features=plan.features if isinstance(plan.features, list) else [],
        is_active=plan.is_active,
        created_at=plan.created_at
    )

def map_subscription_to_out(sub: Subscription) -> SubscriptionOut:
    today = timezone.now().date()
    days_left = max(0, (sub.end_date - today).days) if sub.status == SubscriptionStatus.ACTIVE else 0
    latest_payment = sub.payments.order_by('-transaction_date').first()
    return SubscriptionOut(
        id=sub.id,
        member_id=sub.member_id,
        member_name=sub.member.full_name,
        member_email=sub.member.email,
        member_phone=sub.member.phone or "",
        plan_id=sub.plan_id,
        plan_name=sub.plan.name,
        plan_price=float(sub.plan.price),
        start_date=sub.start_date,
        end_date=sub.end_date,
        status=sub.status,
        notes=sub.notes or "",
        days_left=days_left,
        payment_status=latest_payment.status if latest_payment else sub.status,
        utr_number=latest_payment.utr_number if latest_payment else "",
        is_verified=(sub.status == SubscriptionStatus.ACTIVE),
        created_at=sub.created_at
    )

def map_payment_to_out(pay: Payment) -> PaymentOut:
    return PaymentOut(
        id=pay.id,
        member_id=pay.member_id,
        member_name=pay.member.full_name,
        member_email=pay.member.email,
        member_phone=pay.member.phone or "",
        subscription_id=pay.subscription_id,
        plan_id=pay.subscription.plan_id if pay.subscription else None,
        plan_name=pay.subscription.plan.name if pay.subscription else None,
        amount=float(pay.amount),
        payment_method=pay.payment_method,
        payment_type=pay.payment_type,
        status=pay.status,
        invoice_number=pay.invoice_number,
        utr_number=pay.utr_number or "",
        upi_vpa=pay.upi_vpa or "",
        rejection_reason=pay.rejection_reason or "",
        verified_at=pay.verified_at,
        transaction_date=pay.transaction_date,
        notes=pay.notes or ""
    )

def map_enquiry_to_out(enq: Enquiry) -> EnquiryOut:
    return EnquiryOut(
        id=enq.id,
        name=enq.name,
        email=enq.email or "",
        phone=enq.phone,
        fitness_goal=enq.fitness_goal or "General Fitness",
        preferred_time=enq.preferred_time or "Morning (6 AM - 10 AM)",
        message=enq.message or "",
        status=enq.status,
        notes=enq.notes or "",
        created_at=enq.created_at
    )

# --- Membership Plans ---
@router.get("/plans", response=List[MembershipPlanOut], auth=None)
def list_plans(request, is_active: Optional[bool] = None):
    qs = MembershipPlan.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return [map_plan_to_out(p) for p in qs.order_by('price')]

@router.post("/plans", response={201: MembershipPlanOut}, auth=jwt_auth)
def create_plan(request, payload: MembershipPlanCreate):
    require_roles(UserRole.ADMIN)(request.auth)
    plan = MembershipPlan.objects.create(
        name=payload.name,
        duration_type=payload.duration_type,
        duration_days=payload.duration_days,
        price=payload.price,
        description=payload.description or "",
        features=payload.features or []
    )
    return 201, map_plan_to_out(plan)

@router.get("/plans/{plan_id}", response=MembershipPlanOut, auth=None)
def get_plan(request, plan_id: int):
    plan = MembershipPlan.objects.filter(id=plan_id).first()
    if not plan:
        raise HttpError(404, "Plan not found")
    return map_plan_to_out(plan)

@router.put("/plans/{plan_id}", response=MembershipPlanOut, auth=jwt_auth)
def update_plan(request, plan_id: int, payload: MembershipPlanUpdate):
    require_roles(UserRole.ADMIN)(request.auth)
    plan = MembershipPlan.objects.filter(id=plan_id).first()
    if not plan:
        raise HttpError(404, "Plan not found")
        
    if payload.name is not None:
        plan.name = payload.name
    if payload.duration_type is not None:
        plan.duration_type = payload.duration_type
    if payload.duration_days is not None:
        plan.duration_days = payload.duration_days
    if payload.price is not None:
        plan.price = payload.price
    if payload.description is not None:
        plan.description = payload.description
    if payload.features is not None:
        plan.features = payload.features
    if payload.is_active is not None:
        plan.is_active = payload.is_active

    plan.save()
    return map_plan_to_out(plan)

@router.delete("/plans/{plan_id}", response={200: dict}, auth=jwt_auth)
def delete_plan(request, plan_id: int):
    require_roles(UserRole.ADMIN)(request.auth)
    plan = MembershipPlan.objects.filter(id=plan_id).first()
    if not plan:
        raise HttpError(404, "Plan not found")
    plan.is_active = False
    plan.save()
    return 200, {"message": f"Plan '{plan.name}' deactivated"}

# --- Subscriptions ---
@router.get("/subscriptions", response=List[SubscriptionOut], auth=jwt_auth)
def list_subscriptions(
    request,
    status: Optional[str] = None,
    member_id: Optional[int] = None,
    expiring_soon_days: Optional[int] = None,
    search: Optional[str] = None
):
    current_user = request.auth
    qs = Subscription.objects.select_related('member', 'plan').all()

    # Member can only see their own subscriptions
    if current_user.role == UserRole.MEMBER:
        qs = qs.filter(member=current_user)
    elif member_id:
        qs = qs.filter(member_id=member_id)

    if status:
        qs = qs.filter(status=status)

    if expiring_soon_days:
        today = timezone.now().date()
        cutoff = today + timedelta(days=expiring_soon_days)
        qs = qs.filter(status=SubscriptionStatus.ACTIVE, end_date__gte=today, end_date__lte=cutoff)

    if search:
        qs = qs.filter(
            Q(member__first_name__icontains=search) |
            Q(member__last_name__icontains=search) |
            Q(member__email__icontains=search) |
            Q(plan__name__icontains=search)
        )

    # Auto-update status for expired ones
    today = timezone.now().date()
    for sub in qs:
        if sub.end_date < today and sub.status == SubscriptionStatus.ACTIVE:
            sub.status = SubscriptionStatus.EXPIRED
            sub.save(update_fields=['status'])

    return [map_subscription_to_out(s) for s in qs.order_by('-id')]

@router.get("/subscriptions/my-active", response=Optional[SubscriptionOut], auth=jwt_auth)
def get_my_active_subscription(request):
    current_user = request.auth
    sub = Subscription.objects.select_related('member', 'plan').filter(
        member=current_user,
        status=SubscriptionStatus.ACTIVE
    ).first()
    if not sub:
        # Fallback to latest expired/recent
        sub = Subscription.objects.select_related('member', 'plan').filter(member=current_user).order_by('-end_date').first()
    if not sub:
        return None
    return map_subscription_to_out(sub)

@router.post("/subscriptions/renew/{subscription_id}", response=SubscriptionOut, auth=jwt_auth)
def renew_subscription(request, subscription_id: int, payload: SubscriptionRenew):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)(request.auth)
    sub = Subscription.objects.select_related('member', 'plan').filter(id=subscription_id).first()
    if not sub:
        raise HttpError(404, "Subscription not found")

    plan = MembershipPlan.objects.filter(id=payload.plan_id).first()
    if not plan:
        raise HttpError(404, "Plan not found")

    today = timezone.now().date()
    start_date = max(today, sub.end_date) if sub.status == SubscriptionStatus.ACTIVE else today
    end_date = start_date + timedelta(days=plan.duration_days)

    with transaction.atomic():
        sub.plan = plan
        sub.start_date = start_date
        sub.end_date = end_date
        sub.status = SubscriptionStatus.ACTIVE
        if payload.notes:
            sub.notes = f"{sub.notes}\nRenewal: {payload.notes}".strip()
        sub.save()

        # Record payment
        amount = payload.amount if payload.amount is not None else float(plan.price)
        Payment.objects.create(
            member=sub.member,
            subscription=sub,
            amount=amount,
            payment_method=payload.payment_method,
            payment_type=PaymentType.RENEWAL,
            status=PaymentStatus.COMPLETED,
            notes=f"Renewal for {plan.name}"
        )

    return map_subscription_to_out(sub)

# --- Unified Member Onboarding (Atomic Transaction) ---
@router.post("/onboard-member", response={201: dict}, auth=jwt_auth)
def onboard_member(request, payload: MemberOnboardSchema):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)(request.auth)

    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "A user with this email already exists")

    plan = MembershipPlan.objects.filter(id=payload.plan_id).first()
    if not plan:
        raise HttpError(404, "Selected membership plan not found")

    branch = None
    if payload.branch_id:
        branch = Branch.objects.filter(id=payload.branch_id).first()
    elif request.auth.branch:
        branch = request.auth.branch

    with transaction.atomic():
        # 1. Create User
        user = User.objects.create_user(
            email=payload.email,
            password=payload.password or "GymMember@2026",
            first_name=payload.first_name,
            last_name=payload.last_name or "",
            phone=payload.phone,
            role=UserRole.MEMBER,
            branch=branch
        )

        # 2. Create Subscription
        start_date = payload.start_date or timezone.now().date()
        end_date = start_date + timedelta(days=plan.duration_days)
        subscription = Subscription.objects.create(
            member=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status=SubscriptionStatus.ACTIVE,
            notes="Initial subscription onboarded at reception"
        )

        # 3. Create Payment
        amount = payload.amount_paid if payload.amount_paid is not None else float(plan.price)
        payment = Payment.objects.create(
            member=user,
            subscription=subscription,
            amount=amount,
            payment_method=payload.payment_method,
            payment_type=PaymentType.INITIAL,
            status=PaymentStatus.COMPLETED,
            notes=payload.payment_notes or "Initial registration payment"
        )

    return 201, {
        "message": "Member onboarded successfully",
        "member_id": user.id,
        "subscription_id": subscription.id,
        "invoice_number": payment.invoice_number,
        "amount": float(payment.amount),
        "end_date": str(subscription.end_date)
    }

# --- Payments ---
@router.get("/payments", response=List[PaymentOut], auth=jwt_auth)
def list_payments(
    request,
    member_id: Optional[int] = None,
    payment_type: Optional[str] = None,
    status: Optional[str] = None
):
    current_user = request.auth
    qs = Payment.objects.select_related('member', 'subscription', 'subscription__plan').all()

    if current_user.role == UserRole.MEMBER:
        qs = qs.filter(member=current_user)
    elif member_id:
        qs = qs.filter(member_id=member_id)

    if payment_type:
        qs = qs.filter(payment_type=payment_type)
    if status:
        qs = qs.filter(status=status)

    return [map_payment_to_out(p) for p in qs.order_by('-transaction_date')]

@router.post("/payments", response={201: PaymentOut}, auth=jwt_auth)
def create_payment(request, payload: PaymentCreate):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)(request.auth)
    member = User.objects.filter(id=payload.member_id).first()
    if not member:
        raise HttpError(404, "Member not found")

    subscription = None
    if payload.subscription_id:
        subscription = Subscription.objects.filter(id=payload.subscription_id).first()

    payment = Payment.objects.create(
        member=member,
        subscription=subscription,
        amount=payload.amount,
        payment_method=payload.payment_method,
        payment_type=payload.payment_type,
        status=payload.status,
        utr_number=payload.utr_number or "",
        notes=payload.notes or ""
    )
    return 201, map_payment_to_out(payment)

# --- Member UTR Submission & Payment Proof ---
@router.post("/payments/submit-utr", response=PaymentOut, auth=jwt_auth)
def submit_utr(request, payload: SubmitUTRRequest):
    user = request.auth
    plan = MembershipPlan.objects.filter(id=payload.plan_id).first()
    if not plan:
        raise HttpError(404, "Plan not found")

    with transaction.atomic():
        # Find or create a subscription for this member
        subscription = Subscription.objects.filter(member=user, plan=plan).order_by('-created_at').first()
        today = timezone.now().date()
        if not subscription:
            subscription = Subscription.objects.create(
                member=user,
                plan=plan,
                start_date=today,
                end_date=today + timedelta(days=plan.duration_days),
                status=SubscriptionStatus.PENDING_VERIFICATION,
                notes="Online registration - awaiting UTR confirmation"
            )
        else:
            subscription.status = SubscriptionStatus.PENDING_VERIFICATION
            subscription.save()

        # Check if existing pending payment exists or create new
        payment = Payment.objects.filter(
            member=user,
            subscription=subscription,
            status=PaymentStatus.PENDING_VERIFICATION
        ).first()

        if payment:
            payment.utr_number = payload.utr_number
            payment.upi_vpa = payload.upi_vpa or "setfit@upi"
            payment.amount = plan.price
            payment.notes = payload.notes or "UTR resubmitted by member"
            payment.save()
        else:
            payment = Payment.objects.create(
                member=user,
                subscription=subscription,
                amount=plan.price,
                payment_method=PaymentMethod.UPI,
                payment_type=PaymentType.INITIAL,
                status=PaymentStatus.PENDING_VERIFICATION,
                utr_number=payload.utr_number,
                upi_vpa=payload.upi_vpa or "setfit@upi",
                notes=payload.notes or "Online UPI Payment Proof submitted"
            )

    return map_payment_to_out(payment)

# --- Admin / Receptionist Verification Queue ---
@router.get("/payments/pending-verifications", response=List[PaymentOut], auth=jwt_auth)
def list_pending_verifications(request):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)(request.auth)
    qs = Payment.objects.filter(
        status=PaymentStatus.PENDING_VERIFICATION
    ).select_related('member', 'subscription', 'subscription__plan').order_by('-transaction_date')
    return [map_payment_to_out(p) for p in qs]

@router.post("/payments/verify/{payment_id}", response=PaymentOut, auth=jwt_auth)
def verify_payment(request, payment_id: int, payload: VerifyPaymentRequest = None):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)(request.auth)
    payment = Payment.objects.select_related('subscription', 'subscription__plan', 'member').filter(id=payment_id).first()
    if not payment:
        raise HttpError(404, "Payment record not found")

    with transaction.atomic():
        payment.status = PaymentStatus.COMPLETED
        payment.verified_by = request.auth
        payment.verified_at = timezone.now()
        if payload and payload.notes:
            payment.notes = f"{payment.notes}\nVerified: {payload.notes}".strip()
        payment.save()

        if payment.subscription:
            today = timezone.now().date()
            plan = payment.subscription.plan
            payment.subscription.status = SubscriptionStatus.ACTIVE
            payment.subscription.start_date = today
            payment.subscription.end_date = today + timedelta(days=plan.duration_days)
            payment.subscription.notes = f"{payment.subscription.notes}\nVerified on {today}".strip()
            payment.subscription.save()

    return map_payment_to_out(payment)

@router.post("/payments/reject/{payment_id}", response=PaymentOut, auth=jwt_auth)
def reject_payment(request, payment_id: int, payload: RejectPaymentRequest):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)(request.auth)
    payment = Payment.objects.filter(id=payment_id).first()
    if not payment:
        raise HttpError(404, "Payment record not found")

    with transaction.atomic():
        payment.status = PaymentStatus.REJECTED
        payment.rejection_reason = payload.reason
        payment.verified_by = request.auth
        payment.verified_at = timezone.now()
        payment.save()

        if payment.subscription:
            payment.subscription.status = SubscriptionStatus.PENDING
            payment.subscription.notes = f"{payment.subscription.notes}\nPayment Rejected: {payload.reason}".strip()
            payment.subscription.save()

    return map_payment_to_out(payment)

# --- Public Enquiries & Lead Management ---
@router.post("/enquiries", response={201: EnquiryOut}, auth=None)
def create_enquiry(request, payload: EnquiryCreate):
    enquiry = Enquiry.objects.create(
        name=payload.name,
        email=payload.email or "",
        phone=payload.phone,
        fitness_goal=payload.fitness_goal or "General Fitness",
        preferred_time=payload.preferred_time or "Morning (6 AM - 10 AM)",
        message=payload.message or "",
        status=EnquiryStatus.NEW
    )
    return 201, map_enquiry_to_out(enquiry)

@router.get("/enquiries", response=List[EnquiryOut], auth=jwt_auth)
def list_enquiries(request, status: Optional[str] = None):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)(request.auth)
    qs = Enquiry.objects.all()
    if status:
        qs = qs.filter(status=status)
    return [map_enquiry_to_out(e) for e in qs.order_by('-created_at')]

@router.patch("/enquiries/{enquiry_id}", response=EnquiryOut, auth=jwt_auth)
def update_enquiry_status(request, enquiry_id: int, payload: EnquiryStatusUpdate):
    require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)(request.auth)
    enquiry = Enquiry.objects.filter(id=enquiry_id).first()
    if not enquiry:
        raise HttpError(404, "Enquiry lead not found")

    enquiry.status = payload.status
    if payload.notes:
        enquiry.notes = payload.notes
    enquiry.save()
    return map_enquiry_to_out(enquiry)

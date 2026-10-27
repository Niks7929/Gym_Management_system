from datetime import datetime, date, timedelta
import urllib.parse
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.membership import MembershipPlan, Membership, Payment
from app.models.training import WorkoutPlan, DietPlan, TrainerMemberAssignment
from app.models.attendance import Attendance
from app.models.operations import GymSetting
from app.services.security import role_required
from app.services.audit import log_audit_event

member_bp = Blueprint('member', __name__)

@member_bp.before_request
@login_required
@role_required(['member', 'admin'])
def enforce_member_access():
    pass

@member_bp.route('/')
@member_bp.route('/dashboard')
def dashboard():
    profile = current_user.member_profile
    if not profile:
        flash('Member profile not found.', 'danger')
        return redirect(url_for('auth.portal'))

    # Active or latest membership
    membership = profile.active_membership or (profile.memberships[-1] if profile.memberships else None)
    
    # Check if pending verification or renewal is needed
    is_pending = membership and membership.status == 'pending_verification'
    is_expiring_soon = membership and membership.status == 'active' and membership.days_remaining <= 3

    # Assigned workout & diet
    workout = WorkoutPlan.query.filter_by(member_id=profile.id, is_active=True).order_by(WorkoutPlan.id.desc()).first()
    diet = DietPlan.query.filter_by(member_id=profile.id, is_active=True).order_by(DietPlan.id.desc()).first()
    
    # Coach assignment
    assignment = TrainerMemberAssignment.query.filter_by(member_id=profile.id, is_active=True).first()
    trainer = assignment.trainer if assignment else None

    # Attendance streak
    month_start = date(date.today().year, date.today().month, 1)
    monthly_visits = Attendance.query.filter(Attendance.member_id == profile.id, Attendance.date >= month_start).count()
    
    # UPI QR URL generation
    settings = GymSetting.query.first()
    upi_id = settings.upi_id if settings and settings.upi_id else 'setfit@upi'
    plan_name = membership.plan.name if membership and membership.plan else 'SETFIT_PASS'
    amount = membership.amount_paid if membership else 6000.0
    
    upi_payload = f"upi://pay?pa={urllib.parse.quote(upi_id)}&pn=SETFIT_GYM&am={amount}&cu=INR&tn={urllib.parse.quote(f'Pass_{plan_name}')}"
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={urllib.parse.quote(upi_payload)}&margin=8"

    # All plans for tier upgrades
    plans = MembershipPlan.query.filter_by(is_active=True).order_by(MembershipPlan.price.asc()).all()

    return render_template(
        'member/dashboard.html',
        profile=profile,
        membership=membership,
        is_pending=is_pending,
        is_expiring_soon=is_expiring_soon,
        workout=workout,
        diet=diet,
        trainer=trainer,
        monthly_visits=monthly_visits,
        upi_id=upi_id,
        qr_code_url=qr_code_url,
        plans=plans
    )

@member_bp.route('/submit-utr', methods=['POST'])
def submit_utr():
    profile = current_user.member_profile
    if not profile:
        return redirect(url_for('member.dashboard'))

    utr_number = request.form.get('utr_number', '').strip()
    plan_id = request.form.get('plan_id', type=int)
    notes = request.form.get('notes', '')

    if not utr_number:
        flash('Please enter your 12-digit UPI UTR / Transaction Reference number.', 'danger')
        return redirect(url_for('member.dashboard'))

    selected_plan = MembershipPlan.query.get(plan_id) if plan_id else None
    
    # Get or create pending membership
    membership = profile.memberships[-1] if profile.memberships else None
    if not membership or membership.status in ['expired', 'cancelled']:
        days = selected_plan.duration_days if selected_plan else 30
        membership = Membership(
            member_id=profile.id,
            plan_id=selected_plan.id if selected_plan else 1,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=days),
            status='pending_verification',
            is_verified=False,
            amount_paid=selected_plan.price if selected_plan else 0.0
        )
        db.session.add(membership)
        db.session.flush()

    membership.status = 'pending_verification'
    membership.utr_number = utr_number
    if selected_plan:
        membership.plan_id = selected_plan.id
        membership.amount_paid = selected_plan.price

    # Record or update payment record
    payment = Payment.query.filter_by(membership_id=membership.id, status='pending_verification').first()
    if not payment:
        payment = Payment(
            invoice_number=f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:18]}-{profile.id:04d}",
            member_id=profile.id,
            membership_id=membership.id,
            amount=membership.amount_paid,
            payment_method='upi',
            payment_type='initial' if not profile.payments else 'renewal'
        )
        db.session.add(payment)

    payment.status = 'pending_verification'
    payment.utr_number = utr_number
    payment.notes = f"UTR submitted by athlete: {notes}" if notes else "UTR proof submitted online"
    payment.transaction_date = datetime.utcnow()
    
    db.session.commit()
    log_audit_event('MEMBER_SUBMITTED_UTR', f"Member {current_user.email} submitted UTR: {utr_number}", current_user)
    flash('Transaction reference submitted successfully! Front-desk will verify and activate your 24/7 pass shortly.', 'success')
    return redirect(url_for('member.dashboard'))

@member_bp.route('/workout')
def workout():
    profile = current_user.member_profile
    workout_plan = WorkoutPlan.query.filter_by(member_id=profile.id, is_active=True).order_by(WorkoutPlan.id.desc()).first()
    return render_template('member/workout.html', profile=profile, workout=workout_plan)

@member_bp.route('/diet')
def diet():
    profile = current_user.member_profile
    diet_plan = DietPlan.query.filter_by(member_id=profile.id, is_active=True).order_by(DietPlan.id.desc()).first()
    return render_template('member/diet.html', profile=profile, diet=diet_plan)

@member_bp.route('/attendance')
def attendance():
    profile = current_user.member_profile
    attendances_list = Attendance.query.filter_by(member_id=profile.id).order_by(Attendance.date.desc()).all()
    return render_template('member/attendance.html', profile=profile, attendances=attendances_list)

@member_bp.route('/payments')
def payments():
    profile = current_user.member_profile
    if not profile:
        flash('Member profile not found.', 'danger')
        return redirect(url_for('member.dashboard'))
    payments_list = Payment.query.filter_by(member_id=profile.id).order_by(Payment.transaction_date.desc()).all()
    membership = profile.active_membership or (profile.memberships[-1] if profile.memberships else None)
    plans = MembershipPlan.query.filter_by(is_active=True).order_by(MembershipPlan.price.asc()).all()
    settings = GymSetting.query.first()
    return render_template('member/payments.html', profile=profile, payments=payments_list, membership=membership, plans=plans, gym_settings=settings)


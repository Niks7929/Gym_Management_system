from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models.user import User, Role, MemberProfile, TrainerProfile
from app.models.membership import MembershipPlan, Membership, Payment, Enquiry
from app.models.attendance import Attendance
from app.models.training import TrainerMemberAssignment, WorkoutPlan, DietPlan
from app.models.operations import Equipment, EquipmentMaintenance, GymSetting
from app.models.security import AuditLog
from app.services.security import role_required
from app.services.audit import log_audit_event

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
@role_required('admin')
def enforce_admin_access():
    pass

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    today = date.today()
    
    total_members = MemberProfile.query.count()
    active_members = Membership.query.filter(
        Membership.status == 'active',
        Membership.start_date <= today,
        Membership.end_date >= today
    ).count()
    
    expired_members = Membership.query.filter(
        (Membership.status == 'expired') | (Membership.end_date < today)
    ).count()
    
    total_trainers = TrainerProfile.query.count()
    
    today_checkins = Attendance.query.filter_by(date=today).count()
    
    # Revenue calculations
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(Payment.status == 'completed').scalar() or 0.0
    
    first_day_this_month = date(today.year, today.month, 1)
    month_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        Payment.transaction_date >= datetime.combine(first_day_this_month, datetime.min.time())
    ).scalar() or 0.0
    
    # Pending UTR approvals count
    pending_utrs = Payment.query.filter_by(status='pending_verification').count()
    
    # Recent leads
    new_leads_count = Enquiry.query.filter_by(status='new').count()

    # Monthly revenue trend (last 6 months)
    revenue_chart_labels = []
    revenue_chart_data = []
    for i in range(5, -1, -1):
        m_date = today.replace(day=1) - timedelta(days=i * 30)
        m_start = datetime(m_date.year, m_date.month, 1)
        if m_date.month == 12:
            m_end = datetime(m_date.year + 1, 1, 1)
        else:
            m_end = datetime(m_date.year, m_date.month + 1, 1)
            
        m_rev = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.transaction_date >= m_start,
            Payment.transaction_date < m_end
        ).scalar() or 0.0
        
        revenue_chart_labels.append(m_start.strftime('%b %Y'))
        revenue_chart_data.append(round(m_rev, 2))

    recent_audits = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        total_members=total_members,
        active_members=active_members,
        total_active_members=active_members,
        expired_members=expired_members,
        total_trainers=total_trainers,
        today_checkins=today_checkins,
        total_revenue=total_revenue,
        month_revenue=month_revenue,
        pending_utrs=pending_utrs,
        pending_payments_count=pending_utrs,
        new_leads_count=new_leads_count,
        chart_labels=revenue_chart_labels,
        chart_data=revenue_chart_data,
        chart_months=revenue_chart_labels,
        chart_revenues=revenue_chart_data,
        recent_audits=recent_audits
    )

# --- Member Management ---
@admin_bp.route('/members')
def members():
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    
    query = MemberProfile.query.join(User)
    
    if search:
        query = query.filter(
            (User.first_name.ilike(f"%{search}%")) |
            (User.last_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.phone.ilike(f"%{search}%"))
        )
        
    members_list = query.order_by(MemberProfile.id.desc()).all()
    plans = MembershipPlan.query.filter_by(is_active=True).all()
    
    return render_template('admin/members.html', members=members_list, plans=plans, status_filter=status_filter, search=search)

@admin_bp.route('/members/add', methods=['POST'])
def add_member():
    email = request.form.get('email', '').strip().lower()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', 'SetfitMember2026!')
    plan_id = request.form.get('plan_id', type=int)
    
    if User.query.filter_by(email=email).first():
        flash('A user with this email already exists.', 'danger')
        return redirect(url_for('admin.members'))
        
    role = Role.query.filter_by(name='member').first()
    user = User(
        email=email,
        role_id=role.id,
        role='member',
        first_name=first_name,
        last_name=last_name,
        phone=phone
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    
    profile = MemberProfile(user_id=user.id)
    db.session.add(profile)
    db.session.flush()
    
    if plan_id:
        plan = MembershipPlan.query.get(plan_id)
        if plan:
            mem = Membership(
                member_id=profile.id,
                plan_id=plan.id,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=plan.duration_days),
                status='active',
                is_verified=True,
                amount_paid=plan.price
            )
            db.session.add(mem)
            db.session.flush()
            
            pay = Payment(
                invoice_number=f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:18]}-{profile.id:04d}",
                member_id=profile.id,
                membership_id=mem.id,
                amount=plan.price,
                payment_method='cash',
                payment_type='initial',
                status='completed',
                notes='Direct onboard by Admin'
            )
            db.session.add(pay)
            
    db.session.commit()
    log_audit_event('ADMIN_CREATED_MEMBER', f"Created member account for {email}", current_user)
    flash(f"Member account created for {first_name} {last_name}.", 'success')
    return redirect(url_for('admin.members'))

@admin_bp.route('/members/toggle-block/<int:user_id>', methods=['POST'])
@admin_bp.route('/members/toggle-status/<int:user_id>', methods=['POST'])
@admin_bp.route('/users/toggle-status/<int:user_id>', methods=['POST'])
def toggle_block_member(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = not user.is_blocked
    user.is_active = not user.is_blocked
    db.session.commit()
    status_str = 'Blocked' if user.is_blocked else 'Unblocked'
    log_audit_event('ADMIN_TOGGLED_USER_BLOCK', f"User {user.email} set to {status_str}", current_user)
    flash(f"User {user.email} is now {status_str}.", 'info')
    return redirect(request.referrer or url_for('admin.members'))

@admin_bp.route('/users/toggle-user-status/<int:user_id>', methods=['POST'])
def toggle_user_status(user_id):
    return toggle_block_member(user_id)

@admin_bp.route('/members/delete/<int:user_id>', methods=['POST'])
def delete_member(user_id):
    user = User.query.get(user_id)
    if not user:
        m_prof = MemberProfile.query.get(user_id)
        if m_prof:
            user = m_prof.user

    if not user:
        flash('Member account not found.', 'danger')
        return redirect(url_for('admin.members'))

    email = user.email
    if user.member_profile:
        mem_id = user.member_profile.id
        Attendance.query.filter_by(member_id=mem_id).delete()
        Payment.query.filter_by(member_id=mem_id).delete()
        Membership.query.filter_by(member_id=mem_id).delete()
        TrainerMemberAssignment.query.filter_by(member_id=mem_id).delete()
        WorkoutPlan.query.filter_by(member_id=mem_id).delete()
        DietPlan.query.filter_by(member_id=mem_id).delete()
        db.session.delete(user.member_profile)
    db.session.delete(user)
    db.session.commit()
    log_audit_event('ADMIN_DELETED_MEMBER', f"Permanently deleted member account: {email}", current_user)
    flash(f"Member account '{email}' deleted permanently.", 'danger')
    return redirect(request.referrer or url_for('admin.members'))

# --- Trainers Management ---
@admin_bp.route('/trainers')
def trainers():
    trainers_list = TrainerProfile.query.join(User).all()
    return render_template('admin/trainers.html', trainers=trainers_list)

@admin_bp.route('/trainers/add', methods=['GET', 'POST'])
def add_trainer():
    if request.method == 'GET':
        return redirect(url_for('admin.trainers'))

    email = request.form.get('email', '').strip().lower()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', 'CoachSetFit2026!')
    specialization = request.form.get('specialization', 'Master Strength Coach')
    experience = request.form.get('experience_years', type=int) or 2
    hourly_rate = request.form.get('hourly_rate', type=float) or 600.0
    bio = request.form.get('bio', '')
    
    if User.query.filter_by(email=email).first():
        flash('An account with this email already exists.', 'danger')
        return redirect(url_for('admin.trainers'))
        
    role = Role.query.filter_by(name='trainer').first()
    if not role:
        role = Role(name='trainer', description='Gym Trainer')
        db.session.add(role)
        db.session.commit()
        
    user = User(
        email=email,
        role_id=role.id,
        role='trainer',
        first_name=first_name,
        last_name=last_name,
        phone=phone
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    
    profile = TrainerProfile(
        user_id=user.id,
        specialization=specialization,
        experience_years=experience,
        hourly_rate=hourly_rate,
        bio=bio
    )
    db.session.add(profile)
    db.session.commit()
    
    log_audit_event('ADMIN_CREATED_TRAINER', f"Created trainer account for {email}", current_user)
    flash(f"Master Coach {first_name} {last_name} created successfully.", 'success')
    return redirect(url_for('admin.trainers'))

@admin_bp.route('/trainers/create', methods=['GET', 'POST'])
def create_trainer():
    return add_trainer()

# --- Membership Plans CRUD ---
@admin_bp.route('/plans')
def plans():
    plans_list = MembershipPlan.query.order_by(MembershipPlan.price.asc()).all()
    return render_template('admin/plans.html', plans=plans_list)

@admin_bp.route('/plans/add', methods=['POST'])
def add_plan():
    name = request.form.get('name', '').strip()
    duration_months = request.form.get('duration_months', type=int) or 1
    duration_days = request.form.get('duration_days', type=int) or (duration_months * 30)
    price = request.form.get('price', type=float) or 1600.0
    description = request.form.get('description', '')
    features_raw = request.form.get('features', '')
    features = [f.strip() for f in features_raw.split(',') if f.strip()]
    
    # Check for duplicate active plan
    existing = MembershipPlan.query.filter(
        db.func.lower(MembershipPlan.name) == name.lower(),
        MembershipPlan.duration_months == duration_months,
        MembershipPlan.is_active == True
    ).first()
    
    if existing:
        flash('An active membership plan with this name and duration already exists. Please update the existing plan instead of creating a duplicate.', 'warning')
        return redirect(url_for('admin.plans'))
    
    plan = MembershipPlan(
        name=name,
        duration_months=duration_months,
        duration_days=duration_days,
        price=price,
        description=description,
        is_active=True
    )
    plan.set_features(features)
    db.session.add(plan)
    db.session.commit()
    
    log_audit_event('ADMIN_CREATED_PLAN', f"Created plan {name} at ₹{price}", current_user)
    flash(f"Membership Package {name} created successfully!", 'success')
    return redirect(url_for('admin.plans'))

@admin_bp.route('/plans/edit/<int:plan_id>', methods=['POST'])
def edit_plan(plan_id):
    plan = MembershipPlan.query.get_or_404(plan_id)
    name = request.form.get('name', '').strip() or plan.name
    price = request.form.get('price', type=float) or plan.price
    duration_months = request.form.get('duration_months', type=int) or plan.duration_months
    duration_days = request.form.get('duration_days', type=int) or (duration_months * 30)
    description = request.form.get('description', plan.description)
    features_raw = request.form.get('features', '')
    
    # Check duplicate if renaming/changing duration
    existing = MembershipPlan.query.filter(
        MembershipPlan.id != plan.id,
        db.func.lower(MembershipPlan.name) == name.lower(),
        MembershipPlan.duration_months == duration_months,
        MembershipPlan.is_active == True
    ).first()
    
    if existing:
        flash('Another active plan with this name and duration already exists.', 'warning')
        return redirect(url_for('admin.plans'))
        
    plan.name = name
    plan.price = price
    plan.duration_months = duration_months
    plan.duration_days = duration_days
    plan.description = description
    if features_raw:
        plan.set_features([f.strip() for f in features_raw.split(',') if f.strip()])
        
    db.session.commit()
    log_audit_event('ADMIN_UPDATED_PLAN', f"Updated plan {name} (ID: {plan.id})", current_user)
    flash(f"Plan {plan.name} updated successfully.", 'success')
    return redirect(url_for('admin.plans'))

@admin_bp.route('/plans/update/<int:plan_id>', methods=['POST'])
def update_plan(plan_id):
    return edit_plan(plan_id)

@admin_bp.route('/plans/toggle/<int:plan_id>', methods=['POST'])
def toggle_plan(plan_id):
    plan = MembershipPlan.query.get_or_404(plan_id)
    plan.is_active = not plan.is_active
    db.session.commit()
    flash(f"Plan {plan.name} status updated.", 'info')
    return redirect(url_for('admin.plans'))

# --- Revenue & Payments ---
@admin_bp.route('/payments')
def payments():
    payments_list = Payment.query.order_by(Payment.transaction_date.desc()).all()
    pending_list = Payment.query.filter_by(status='pending_verification').all()
    completed_list = Payment.query.filter(Payment.status != 'pending_verification').order_by(Payment.transaction_date.desc()).all()
    return render_template('admin/payments.html', payments=payments_list, pending_payments=pending_list, completed_payments=completed_list)

@admin_bp.route('/payments/verify/<int:payment_id>', methods=['POST'])
def verify_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    payment.status = 'completed'
    payment.verified_by_id = current_user.id
    
    # Activate membership
    if payment.membership:
        payment.membership.status = 'active'
        payment.membership.is_verified = True
        plan = payment.membership.plan
        if plan:
            payment.membership.start_date = date.today()
            payment.membership.end_date = date.today() + timedelta(days=plan.duration_days)
            
    db.session.commit()
    log_audit_event('ADMIN_VERIFIED_PAYMENT', f"Payment {payment.invoice_number} verified and activated for member {payment.member_id}", current_user)
    flash(f"Payment {payment.invoice_number} verified! Member pass activated.", 'success')
    return redirect(url_for('admin.payments'))

@admin_bp.route('/payments/reject/<int:payment_id>', methods=['POST'])
def reject_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    reason = request.form.get('reason', 'Payment reference / UTR not received in bank statement')
    payment.status = 'rejected'
    payment.rejection_reason = reason
    
    if payment.membership:
        payment.membership.status = 'cancelled'
        
    db.session.commit()
    log_audit_event('ADMIN_REJECTED_PAYMENT', f"Payment {payment.invoice_number} rejected. Reason: {reason}", current_user)
    flash(f"Payment {payment.invoice_number} rejected.", 'warning')
    return redirect(url_for('admin.payments'))

# --- Leads & Enquiries ---
@admin_bp.route('/enquiries')
def enquiries():
    status_filter = request.args.get('status', 'all')
    if status_filter != 'all':
        enquiries_list = Enquiry.query.filter_by(status=status_filter).order_by(Enquiry.created_at.desc()).all()
    else:
        enquiries_list = Enquiry.query.order_by(Enquiry.created_at.desc()).all()
        
    return render_template('admin/enquiries.html', enquiries=enquiries_list, status_filter=status_filter)

@admin_bp.route('/enquiries/update-status/<int:enquiry_id>', methods=['POST'])
def update_enquiry_status(enquiry_id):
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    new_status = request.form.get('status', 'contacted')
    enquiry.status = new_status
    db.session.commit()
    flash(f"Lead status updated to {new_status.title()}.", 'success')
    return redirect(url_for('admin.enquiries'))

# --- Equipment & Maintenance ---
@admin_bp.route('/equipment')
def equipment():
    equipment_list = Equipment.query.all()
    maintenances = EquipmentMaintenance.query.order_by(EquipmentMaintenance.maintenance_date.desc()).all()
    return render_template('admin/equipment.html', equipment=equipment_list, equipment_list=equipment_list, maintenances=maintenances)

@admin_bp.route('/equipment/add', methods=['POST'])
def add_equipment():
    name = request.form.get('name', '').strip()
    category = request.form.get('category', 'Free Weights')
    serial = request.form.get('serial_number', '').strip() or None
    location = request.form.get('location', 'Main Arena')
    
    eq = Equipment(name=name, category=category, serial_number=serial, location=location)
    db.session.add(eq)
    db.session.commit()
    flash(f"Equipment {name} registered.", 'success')
    return redirect(url_for('admin.equipment'))

@admin_bp.route('/equipment/toggle-status/<int:equip_id>', methods=['POST'])
@admin_bp.route('/equipment/update-status/<int:equip_id>', methods=['POST'])
def update_equipment_status(equip_id):
    eq = Equipment.query.get_or_404(equip_id)
    new_cond = request.form.get('condition')
    if new_cond:
        eq.status = new_cond
    else:
        eq.status = 'Needs Service' if eq.status == 'Operational' else 'Operational'
    db.session.commit()
    flash(f"Equipment {eq.name} status updated to {eq.status}.", 'info')
    return redirect(url_for('admin.equipment'))

# --- Security Audit Logs ---
@admin_bp.route('/audit-logs')
@admin_bp.route('/audit_logs')
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(150).all()
    return render_template('admin/audit_logs.html', logs=logs, audit_logs=logs)

# --- CMS Settings ---
@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    setting = GymSetting.query.first()
    if not setting:
        setting = GymSetting()
        db.session.add(setting)
        db.session.commit()
        
    if request.method == 'POST':
        setting.gym_name = request.form.get('gym_name', 'SETFIT DARK RAGE')
        setting.tagline = request.form.get('tagline', 'BUILD YOUR POWER. DEFINE YOUR LIMITS.')
        setting.announcement_bar = request.form.get('announcement_bar', '')
        setting.contact_phone = request.form.get('contact_phone') or request.form.get('phone', '+91 98765 43210')
        setting.contact_email = request.form.get('contact_email') or request.form.get('email', 'contact@setfitgym.com')
        setting.address = request.form.get('address', 'Near Pratibha Society, Karve Nagar, Pune, Maharashtra 411052')
        setting.currency_symbol = request.form.get('currency_symbol', '₹')
        setting.upi_id = request.form.get('upi_id', 'setfit@upi')
        
        db.session.commit()
        log_audit_event('ADMIN_UPDATED_SETTINGS', 'Updated gym brand and operational settings', current_user)
        flash('Gym parameters updated and published live.', 'success')
        return redirect(url_for('admin.settings'))
        
    return render_template('admin/settings.html', setting=setting, settings=setting)


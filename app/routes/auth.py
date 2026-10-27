from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User, Role, MemberProfile
from app.models.membership import MembershipPlan, Membership, Payment
from app.forms.auth_forms import LoginForm, AdminLoginForm, MemberRegisterForm
from app.services.audit import log_audit_event
from app.services.security import handle_failed_login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/portal')
def portal():
    """Central login gateway - redirects directly to the unified login page."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'trainer':
            return redirect(url_for('trainer.dashboard'))
        else:
            return redirect(url_for('member.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Single unified authentication for Member, Trainer, and Admin."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'trainer':
            return redirect(url_for('trainer.dashboard'))
        else:
            return redirect(url_for('member.dashboard'))

    form = LoginForm()
    prefill_email = request.args.get('email', '').strip().lower()
    if prefill_email and request.method == 'GET':
        form.email.data = prefill_email

    if form.validate_on_submit() or request.method == 'POST':
        email = (form.email.data or request.form.get('email', '')).strip().lower()
        password = form.password.data or request.form.get('password', '')

        if not email or not password:
            flash('Please enter both your email address and password.', 'danger')
            return render_template('auth/login.html', form=form, prefill_email=prefill_email)

        user = User.query.filter(db.func.lower(User.email) == email).first()

        if not user:
            log_audit_event('FAILED_LOGIN_UNKNOWN_EMAIL', f"Attempted login with non-existent email: {email}")
            flash('Invalid email address or password.', 'danger')
            return render_template('auth/login.html', form=form)

        # Check account lockout
        if user.is_locked():
            lock_mins = int((user.locked_until - datetime.utcnow()).total_seconds() / 60) + 1
            log_audit_event('LOCKED_ACCOUNT_LOGIN_ATTEMPT', f"Attempted login on locked account: {email}", user)
            flash(f'Account temporarily locked due to repeated failed attempts. Please try again in {lock_mins} minutes.', 'danger')
            return render_template('auth/login.html', form=form)

        # Check account blocked status
        if user.is_blocked:
            log_audit_event('BLOCKED_ACCOUNT_LOGIN_ATTEMPT', f"Attempted login on suspended account: {email}", user)
            flash('This account is suspended by gym administration. Please visit the front desk.', 'danger')
            return render_template('auth/login.html', form=form)

        # Check password hash
        if not user.check_password(password):
            handle_failed_login(user)
            flash('Invalid email address or password.', 'danger')
            return render_template('auth/login.html', form=form)

        # Successful Login
        user.reset_failed_attempts()
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = request.remote_addr
        db.session.commit()

        remember = form.remember_me.data if form.remember_me.data is not None else ('remember' in request.form)
        login_user(user, remember=remember)
        log_audit_event('LOGIN_SUCCESS', f"User logged in successfully with role {user.role}", user)

        next_page = request.args.get('next')
        if next_page and not next_page.startswith('http'):
            return redirect(next_page)

        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'trainer':
            return redirect(url_for('trainer.dashboard'))
        else:
            return redirect(url_for('member.dashboard'))

    return render_template('auth/login.html', form=form)

@auth_bp.route('/admin-access', methods=['GET', 'POST'])
def admin_access():
    """Protected Admin Access portal with secondary security passcode."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            flash('You do not possess master administrator privileges.', 'danger')
            return redirect(url_for('auth.portal'))

    form = AdminLoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        passcode = form.admin_secret.data.strip()

        # Check secondary security passcode
        expected_secret = current_app.config.get('ADMIN_SECRET', 'SETFIT_MASTER_ADMIN_PASSCODE_2026')
        if passcode != expected_secret:
            log_audit_event('ADMIN_PASSCODE_FAILED', f"Invalid admin passcode attempt for {email}")
            flash('Security Verification Failed: Invalid Master Admin Passcode.', 'danger')
            return render_template('auth/admin_login.html', form=form)

        user = User.query.filter_by(email=email).first()

        if not user or user.role != 'admin':
            log_audit_event('ADMIN_UNAUTHORIZED_EMAIL', f"Non-admin email attempted admin login: {email}")
            flash('Access Denied: Administrative credentials could not be verified.', 'danger')
            return render_template('auth/admin_login.html', form=form)

        if user.is_locked():
            lock_mins = int((user.locked_until - datetime.utcnow()).total_seconds() / 60) + 1
            log_audit_event('LOCKED_ADMIN_LOGIN_ATTEMPT', f"Attempted login on locked admin account: {email}", user)
            flash(f'Admin terminal locked. Try again in {lock_mins} minutes.', 'danger')
            return render_template('auth/admin_login.html', form=form)

        if not user.check_password(password):
            handle_failed_login(user)
            flash('Access Denied: Invalid Master Admin password.', 'danger')
            return render_template('auth/admin_login.html', form=form)

        # Successful Admin Auth
        user.reset_failed_attempts()
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = request.remote_addr
        db.session.commit()

        login_user(user, remember=False)
        log_audit_event('ADMIN_LOGIN_SUCCESS', 'Master Admin authorized through executive terminal', user)
        flash('Executive Command Authorized. Welcome, Master Admin.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('auth/admin_login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Member-only public registration."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.portal'))

    form = MemberRegisterForm()
    plans = MembershipPlan.query.filter_by(is_active=True).order_by(MembershipPlan.price.asc()).all()
    form.plan_id.choices = [(p.id, f"{p.name} — ₹{int(p.price):,} ({p.duration_months} Months)") for p in plans]

    # Pre-select plan if passed in query string
    plan_id_arg = request.args.get('plan_id', type=int)
    if plan_id_arg and request.method == 'GET':
        form.plan_id.data = plan_id_arg

    if request.method == 'POST':
        selected_role = request.form.get('role', 'member').strip().lower()
        if selected_role not in ['member', 'trainer']:
            selected_role = 'member'
            
        full_name = request.form.get('full_name', '').strip() or f"{request.form.get('first_name', '')} {request.form.get('last_name', '')}".strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        plan_id = request.form.get('plan_id', type=int)

        if not email or not password or not full_name:
            flash('Please complete all required registration fields.', 'danger')
            return render_template('auth/register.html', form=form, plans=plans, selected_plan_id=plan_id_arg)

        existing_user = User.query.filter(db.func.lower(User.email) == email).first()
        if existing_user:
            flash(f"An account for '{email}' already exists. Please enter your password below to sign in.", 'info')
            return redirect(url_for('auth.login', email=email))

        # Ensure role exists in DB
        db_role = Role.query.filter_by(name=selected_role).first()
        if not db_role:
            role_desc = f"Standard {selected_role.title()}"
            db_role = Role(name=selected_role, description=role_desc)
            db.session.add(db_role)
            db.session.commit()

        # Create user account
        new_user = User(
            email=email,
            role_id=db_role.id,
            role=selected_role,
            full_name=full_name,
            phone=phone,
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Create role-specific profile
        if selected_role == 'trainer':
            from app.models.user import TrainerProfile
            profile = TrainerProfile(
                user_id=new_user.id,
                specialization='Fitness & Strength Coach',
                experience_years=2,
                bio='Dedicated fitness coach engineered to help athletes reach peak performance.'
            )
            db.session.add(profile)
            db.session.commit()
            log_audit_event('TRAINER_REGISTERED', f"New coach registered: {email}", new_user)
            login_user(new_user)
            flash('Welcome to SETFIT GYM! Your coach portal account has been established.', 'success')
            return redirect(url_for('trainer.dashboard'))

        else: # member
            profile = MemberProfile(
                user_id=new_user.id,
                fitness_goal='Strength & Conditioning'
            )
            db.session.add(profile)
            db.session.flush()

            # Create Initial Membership
            selected_plan = MembershipPlan.query.get(plan_id) if plan_id else (plans[0] if plans else None)
            plan_days = selected_plan.duration_days if selected_plan else 30
            membership = Membership(
                member_id=profile.id,
                plan_id=selected_plan.id if selected_plan else 1,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=plan_days),
                status='pending_verification',
                is_verified=False,
                amount_paid=selected_plan.price if selected_plan else 0.0
            )
            db.session.add(membership)
            db.session.flush()

            # Create Initial Payment Invoice
            inv_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{profile.id:04d}"
            payment = Payment(
                invoice_number=inv_number,
                member_id=profile.id,
                membership_id=membership.id,
                amount=selected_plan.price if selected_plan else 0.0,
                payment_method='upi',
                payment_type='initial',
                status='pending_verification',
                notes=f"Initial registration for {selected_plan.name if selected_plan else 'Plan'}"
            )
            db.session.add(payment)
            db.session.commit()

            log_audit_event('MEMBER_REGISTERED', f"New athlete registered: {email}", new_user)
            login_user(new_user)
            flash('Welcome to SETFIT GYM! Your member account has been established.', 'success')
            return redirect(url_for('member.dashboard'))

    return render_template('auth/register.html', form=form, plans=plans)

@auth_bp.route('/logout')
@login_required
def logout():
    user = current_user
    log_audit_event('LOGOUT', f"User {user.email} logged out", user)
    logout_user()
    flash('You have been securely signed out.', 'info')
    return redirect(url_for('public.index'))

from datetime import datetime, date, time, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models.user import User, Role, MemberProfile
from app.models.membership import MembershipPlan, Membership, Payment, Enquiry
from app.models.attendance import Attendance
from app.services.security import role_required
from app.services.audit import log_audit_event

receptionist_bp = Blueprint('receptionist', __name__)

@receptionist_bp.before_request
@login_required
@role_required(['receptionist', 'admin'])
def enforce_receptionist_access():
    pass

def get_all_gym_members():
    """Helper to fetch all registered member users."""
    return User.query.filter_by(role='member', is_active=True).all()

@receptionist_bp.route('/')
@receptionist_bp.route('/dashboard')
def dashboard():
    today = date.today()
    today_checkins = Attendance.query.filter_by(date=today).count()
    active_members = Membership.query.filter(
        Membership.status == 'active',
        Membership.start_date <= today,
        Membership.end_date >= today
    ).count()
    
    seven_days = today + timedelta(days=7)
    expiring_soon = Membership.query.filter(
        Membership.status == 'active',
        Membership.end_date >= today,
        Membership.end_date <= seven_days
    ).count()
    
    today_start = datetime.combine(today, datetime.min.time())
    today_intake = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        Payment.transaction_date >= today_start
    ).scalar() or 0.0

    recent_attendances = Attendance.query.filter_by(date=today).order_by(Attendance.check_in_time.desc()).limit(8).all()
    pending_verifications = Payment.query.filter_by(status='pending_verification').all()
    new_leads = Enquiry.query.filter_by(status='new').limit(5).all()

    return render_template(
        'receptionist/dashboard.html',
        today_checkins=today_checkins,
        active_members=active_members,
        expiring_soon=expiring_soon,
        today_intake=today_intake,
        recent_attendances=recent_attendances,
        pending_verifications=pending_verifications,
        new_leads=new_leads
    )

@receptionist_bp.route('/checkin', methods=['GET', 'POST'])
def checkin():
    today = date.today()
    search = request.args.get('search', '').strip()
    
    if request.method == 'POST':
        member_id = request.form.get('member_id', type=int)
        identifier = request.form.get('identifier', '').strip()
        
        member = None
        if member_id:
            member = MemberProfile.query.get(member_id) or MemberProfile.query.filter_by(user_id=member_id).first()
        elif identifier:
            # Match by member_code (SFR-10008 -> id 8 or member_code)
            if identifier.upper().startswith('SFR-'):
                try:
                    code_id = int(identifier.upper().replace('SFR-', '')) - 10000
                    member = MemberProfile.query.get(code_id)
                except Exception:
                    pass
            if not member:
                user = User.query.filter((User.email == identifier.lower()) | (User.phone == identifier)).first()
                if user and user.member_profile:
                    member = user.member_profile
                    
        if not member:
            flash(f"No athlete profile found for '{identifier or member_id}'", 'danger')
            return redirect(url_for('receptionist.checkin'))
            
        # Check if active membership exists
        if not member.active_membership and not member.memberships:
            flash(f"Warning: {member.user.full_name} does not have an active membership pass!", 'danger')
            return redirect(url_for('receptionist.checkin'))

        # Check if already checked in today
        existing = Attendance.query.filter_by(member_id=member.id, date=today).first()
        if existing and not existing.check_out_time:
            # Check out
            existing.check_out_time = datetime.now().time()
            db.session.commit()
            flash(f"Checked out {member.user.full_name} successfully.", 'info')
        elif existing and existing.check_out_time:
            flash(f"{member.user.full_name} has already completed their session today.", 'warning')
        else:
            att = Attendance(
                member_id=member.id,
                date=today,
                check_in_time=datetime.now().time(),
                status='present',
                logged_by_id=current_user.id
            )
            db.session.add(att)
            db.session.commit()
            flash(f"Check-in verified for {member.user.full_name}! 24/7 Access Granted.", 'success')

        return redirect(url_for('receptionist.checkin'))

    members = MemberProfile.query.order_by(MemberProfile.id.desc()).limit(30).all()
    attendances_today = Attendance.query.filter_by(date=today).order_by(Attendance.check_in_time.desc()).all()
    all_members = get_all_gym_members()
    return render_template('receptionist/checkin.html', members=members, attendances=attendances_today, all_members=all_members, search=search)

@receptionist_bp.route('/onboard', methods=['GET', 'POST'])
@receptionist_bp.route('/onboard_member', methods=['POST'])
def onboard():
    plans = MembershipPlan.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        if not first_name and full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
            
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        plan_id = request.form.get('plan_id', type=int)
        payment_method = request.form.get('payment_method', 'cash')
        
        if User.query.filter_by(email=email).first():
            flash('A member with this email address already exists in the system.', 'danger')
            return render_template('receptionist/onboard.html', plans=plans)
            
        role = Role.query.filter_by(name='member').first()
        user = User(
            email=email,
            role_id=role.id,
            role='member',
            first_name=first_name or 'Member',
            last_name=last_name or '',
            phone=phone
        )
        user.set_password('SetfitMember2026!')
        db.session.add(user)
        db.session.flush()
        
        profile = MemberProfile(user_id=user.id, emergency_contact=emergency_contact)
        db.session.add(profile)
        db.session.flush()
        
        selected_plan = MembershipPlan.query.get(plan_id) if plan_id else plans[0]
        days = selected_plan.duration_days if selected_plan else 30
        price = selected_plan.price if selected_plan else 1600.0
        
        membership = Membership(
            member_id=profile.id,
            plan_id=selected_plan.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=days),
            status='active',
            is_verified=True,
            amount_paid=price
        )
        db.session.add(membership)
        db.session.flush()
        
        inv = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{profile.id:04d}"
        payment = Payment(
            invoice_number=inv,
            member_id=profile.id,
            membership_id=membership.id,
            amount=price,
            payment_method=payment_method,
            payment_type='initial',
            status='completed',
            verified_by_id=current_user.id,
            notes='Front desk walk-in registration'
        )
        db.session.add(payment)
        db.session.commit()
        
        log_audit_event('RECEPTIONIST_ONBOARDED_MEMBER', f"Member {email} onboarded with {selected_plan.name}", current_user)
        flash(f"Athlete {user.full_name} onboarded successfully! Invoice {inv} generated.", 'success')
        return redirect(url_for('receptionist.checkin'))

    return render_template('receptionist/onboard.html', plans=plans)

@receptionist_bp.route('/renewals', methods=['GET', 'POST'])
@receptionist_bp.route('/renew_membership', methods=['POST'])
def renewals():
    today = date.today()
    seven_days = today + timedelta(days=7)
    
    expiring_memberships = Membership.query.filter(
        (Membership.end_date <= seven_days) | (Membership.status == 'expired')
    ).order_by(Membership.end_date.asc()).all()
    
    plans = MembershipPlan.query.filter_by(is_active=True).all()
    all_members = get_all_gym_members()

    if request.method == 'POST':
        member_id = request.form.get('member_id', type=int)
        membership_id = request.form.get('membership_id', type=int)
        plan_id = request.form.get('plan_id', type=int)
        payment_method = request.form.get('payment_method', 'cash')
        
        mem = None
        if membership_id:
            mem = Membership.query.get(membership_id)
        elif member_id:
            # Find member profile
            m_prof = MemberProfile.query.filter_by(user_id=member_id).first() or MemberProfile.query.get(member_id)
            if m_prof:
                mem = Membership.query.filter_by(member_id=m_prof.id).order_by(Membership.end_date.desc()).first()
                if not mem:
                    # Create initial membership
                    plan = MembershipPlan.query.get_or_404(plan_id)
                    mem = Membership(
                        member_id=m_prof.id,
                        plan_id=plan.id,
                        start_date=date.today(),
                        end_date=date.today() + timedelta(days=plan.duration_days),
                        status='active',
                        is_verified=True,
                        amount_paid=plan.price
                    )
                    db.session.add(mem)
                    db.session.flush()

        plan = MembershipPlan.query.get_or_404(plan_id)
        
        if mem:
            start_d = date.today() if mem.end_date < date.today() else mem.end_date + timedelta(days=1)
            mem.start_date = start_d
            mem.end_date = start_d + timedelta(days=plan.duration_days)
            mem.plan_id = plan.id
            mem.status = 'active'
            mem.is_verified = True
            mem.amount_paid = plan.price
            
            inv = f"INV-REN-{datetime.utcnow().strftime('%Y%m%d')}-{mem.member_id:04d}"
            payment = Payment(
                invoice_number=inv,
                member_id=mem.member_id,
                membership_id=mem.id,
                amount=plan.price,
                payment_method=payment_method,
                payment_type='renewal',
                status='completed',
                verified_by_id=current_user.id,
                notes='Front desk renewal'
            )
            db.session.add(payment)
            db.session.commit()
            
            log_audit_event('RECEPTIONIST_RENEWED_MEMBERSHIP', f"Renewed membership for member {mem.member_id} with {plan.name}", current_user)
            flash(f"Membership renewed successfully! Pass valid until {mem.end_date.strftime('%d %B %Y')}.", 'success')
        else:
            flash('Member not found.', 'danger')

        return redirect(url_for('receptionist.renewals'))

    return render_template('receptionist/renewals.html', expiring_memberships=expiring_memberships, plans=plans, members=all_members, all_members=all_members)

@receptionist_bp.route('/payments', methods=['GET', 'POST'])
@receptionist_bp.route('/record_payment', methods=['POST'])
def payments():
    if request.method == 'POST':
        raw_user_id = request.form.get('user_id', type=int) or request.form.get('member_id', type=int)
        amount = request.form.get('amount', type=float) or 0.0
        payment_method = request.form.get('payment_method', 'cash')
        notes = request.form.get('transaction_id', '') or request.form.get('notes', 'Counter POS billing')

        if raw_user_id:
            m_prof = MemberProfile.query.filter_by(user_id=raw_user_id).first() or MemberProfile.query.get(raw_user_id)
            if m_prof:
                inv = f"INV-POS-{datetime.utcnow().strftime('%Y%m%d')}-{m_prof.id:04d}"
                
                # Active membership or create default
                active_mem = m_prof.active_membership
                if not active_mem and m_prof.memberships:
                    active_mem = m_prof.memberships[0]
                if active_mem:
                    active_mem.status = 'active'
                    active_mem.is_verified = True
                
                pay = Payment(
                    invoice_number=inv,
                    member_id=m_prof.id,
                    membership_id=active_mem.id if active_mem else None,
                    amount=amount,
                    payment_method=payment_method,
                    payment_type='pos',
                    status='completed',
                    verified_by_id=current_user.id,
                    notes=notes
                )
                db.session.add(pay)
                db.session.commit()
                flash(f"Payment receipt {inv} of ₹{amount:,.0f} issued successfully!", 'success')
            else:
                flash('Member profile not found.', 'danger')
        return redirect(url_for('receptionist.payments'))

    payments_list = Payment.query.order_by(Payment.transaction_date.desc()).limit(50).all()
    pending_list = Payment.query.filter_by(status='pending_verification').all()
    all_members = get_all_gym_members()
    return render_template('receptionist/payments.html', payments=payments_list, pending_payments=pending_list, members=all_members, all_members=all_members)

@receptionist_bp.route('/payments/verify/<int:payment_id>', methods=['POST'])
def verify_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    payment.status = 'completed'
    payment.verified_by_id = current_user.id
    
    if payment.membership:
        payment.membership.status = 'active'
        payment.membership.is_verified = True
        
    db.session.commit()
    log_audit_event('RECEPTIONIST_VERIFIED_PAYMENT', f"Payment {payment.invoice_number} verified by {current_user.full_name}", current_user)
    flash(f"Payment {payment.invoice_number} (UTR: {payment.utr_number or 'N/A'}) verified & activated!", 'success')
    return redirect(url_for('receptionist.payments'))

@receptionist_bp.route('/enquiries')
def enquiries():
    enquiries_list = Enquiry.query.order_by(Enquiry.created_at.desc()).all()
    return render_template('receptionist/enquiries.html', enquiries=enquiries_list)

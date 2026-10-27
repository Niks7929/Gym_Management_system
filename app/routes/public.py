from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.extensions import db
from app.models.membership import MembershipPlan, Enquiry
from app.models.user import User, TrainerProfile
from app.models.operations import GymSetting, Equipment
from app.forms.auth_forms import EnquiryForm
from app.services.audit import log_audit_event

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    # Canonical Active Membership Plans
    plans = MembershipPlan.query.filter_by(is_active=True).order_by(MembershipPlan.price.asc()).all()
    # Active & Unblocked Coaches
    trainers = TrainerProfile.query.join(User).filter(User.is_active == True, User.is_blocked == False).all()
    # Gym equipment / facilities
    equipments = Equipment.query.filter_by(status='Operational').limit(8).all()
    return render_template('public/index.html', plans=plans, trainers=trainers, equipments=equipments)

@public_bp.route('/portal')
def portal_redirect():
    return redirect(url_for('auth.portal'))

@public_bp.route('/member/login')
def member_login_redirect():
    return redirect(url_for('auth.login', role='member'))

@public_bp.route('/trainer/login')
def trainer_login_redirect():
    return redirect(url_for('auth.login', role='trainer'))

@public_bp.route('/about')
def about():
    return redirect(url_for('public.index') + '#about')

@public_bp.route('/facilities')
def facilities():
    equipments = Equipment.query.all()
    return render_template('public/facilities.html', equipments=equipments)

@public_bp.route('/trainers')
def trainers():
    trainers = TrainerProfile.query.join(User).filter(User.is_active == True, User.is_blocked == False).all()
    return render_template('public/trainers.html', trainers=trainers)

@public_bp.route('/plans')
@public_bp.route('/memberships')
def plans():
    plans = MembershipPlan.query.filter_by(is_active=True).order_by(MembershipPlan.price.asc()).all()
    return render_template('public/plans.html', plans=plans)

@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = EnquiryForm()
    if form.validate_on_submit():
        enquiry = Enquiry(
            name=form.name.data.strip(),
            phone=form.phone.data.strip(),
            email=form.email.data.strip() if form.email.data else None,
            preferred_branch=form.preferred_branch.data,
            fitness_goal=form.fitness_goal.data,
            notes=form.notes.data.strip() if form.notes.data else None,
            status='new'
        )
        db.session.add(enquiry)
        db.session.commit()
        flash('Your message has been received! We will connect with you shortly.', 'success')
        return redirect(url_for('public.contact'))
    return render_template('public/contact.html', form=form)

@public_bp.route('/enquiry/submit', methods=['POST'])
def submit_enquiry():
    name = request.form.get('full_name', '').strip() or request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    program = request.form.get('interested_program', '').strip() or request.form.get('fitness_goal', '').strip()
    message = request.form.get('message', '').strip() or request.form.get('notes', '').strip()
    
    if name and phone:
        enquiry = Enquiry(
            name=name,
            phone=phone,
            email=email if email else None,
            fitness_goal=program if program else 'General Strength',
            notes=message if message else None,
            status='new'
        )
        db.session.add(enquiry)
        db.session.commit()
        log_audit_event('PUBLIC_ENQUIRY_SUBMITTED', f"Lead submitted by {name} ({phone})")
        flash('Thank you! Your free strength assessment pass has been reserved. Our coaches will contact you shortly.', 'success')
    else:
        flash('Please provide your name and phone number to claim your pass.', 'danger')
        
    return redirect(url_for('public.index') + '#assessment')

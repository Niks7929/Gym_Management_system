from datetime import datetime, date
import json
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User, MemberProfile, TrainerProfile
from app.models.training import WorkoutPlan, WorkoutExercise, Exercise, DietPlan, DietMeal, TrainerMemberAssignment
from app.models.attendance import Attendance
from app.services.security import role_required
from app.services.audit import log_audit_event

trainer_bp = Blueprint('trainer', __name__)

@trainer_bp.before_request
@login_required
@role_required(['trainer', 'admin'])
def enforce_trainer_access():
    pass

def get_or_create_trainer_profile():
    """Ensure current logged-in trainer user has a valid TrainerProfile."""
    profile = current_user.trainer_profile
    if not profile and current_user.role == 'trainer':
        profile = TrainerProfile(
            user_id=current_user.id,
            specialization="Strength & Conditioning",
            experience_years=3,
            hourly_rate=1200.0,
            bio="Certified fitness coach specializing in strength training, hypertrophy, and nutrition."
        )
        db.session.add(profile)
        db.session.commit()
    return profile

def get_all_gym_members():
    """Fetch all active gym members for selection dropdowns."""
    return User.query.filter_by(role='member', is_active=True).all()

@trainer_bp.route('/')
@trainer_bp.route('/dashboard')
def dashboard():
    profile = get_or_create_trainer_profile()
    trainer_id = profile.id if profile else None

    # Fetch assigned assignments and clients
    assignments = TrainerMemberAssignment.query.filter_by(trainer_id=trainer_id, is_active=True).all() if trainer_id else []
    assigned_clients = [a.member.user for a in assignments if a.member and a.member.user]
    assigned_member_ids = [a.member_id for a in assignments]

    # Fetch workout and diet plans created by this trainer or assigned to their athletes
    workout_plans = WorkoutPlan.query.filter(
        (WorkoutPlan.trainer_id == trainer_id) | (WorkoutPlan.member_id.in_(assigned_member_ids))
    ).order_by(WorkoutPlan.created_at.desc()).all() if trainer_id and assigned_member_ids else (
        WorkoutPlan.query.filter_by(trainer_id=trainer_id).order_by(WorkoutPlan.created_at.desc()).all() if trainer_id else []
    )

    diet_plans = DietPlan.query.filter(
        (DietPlan.trainer_id == trainer_id) | (DietPlan.member_id.in_(assigned_member_ids))
    ).order_by(DietPlan.created_at.desc()).all() if trainer_id and assigned_member_ids else (
        DietPlan.query.filter_by(trainer_id=trainer_id).order_by(DietPlan.created_at.desc()).all() if trainer_id else []
    )

    today = date.today()
    today_checkins = Attendance.query.filter(
        Attendance.member_id.in_(assigned_member_ids), Attendance.date == today
    ).count() if assigned_member_ids else 0

    all_members = get_all_gym_members()

    return render_template(
        'trainer/dashboard.html',
        profile=profile,
        assigned_clients=assigned_clients,
        workout_plans=workout_plans,
        diet_plans=diet_plans,
        assigned_count=len(assigned_clients),
        active_workouts=len(workout_plans),
        active_diets=len(diet_plans),
        today_checkins=today_checkins,
        assignments=assignments,
        all_members=all_members
    )

@trainer_bp.route('/clients')
def clients():
    profile = get_or_create_trainer_profile()
    trainer_id = profile.id if profile else None

    assignments = TrainerMemberAssignment.query.filter_by(trainer_id=trainer_id, is_active=True).all() if trainer_id else []
    assigned_clients = [a.member.user for a in assignments if a.member and a.member.user]
    all_members = get_all_gym_members()

    return render_template(
        'trainer/clients.html',
        clients=assigned_clients,
        assignments=assignments,
        all_members=all_members
    )

@trainer_bp.route('/clients/assign', methods=['POST'])
def assign_client():
    profile = get_or_create_trainer_profile()
    if not profile:
        flash('Trainer profile required.', 'danger')
        return redirect(url_for('trainer.dashboard'))

    raw_id = request.form.get('member_id', type=int)
    notes = request.form.get('notes', 'Assigned via Trainer Portal')

    if raw_id:
        # Check if raw_id is User ID or MemberProfile ID
        member_prof = MemberProfile.query.filter_by(user_id=raw_id).first() or MemberProfile.query.get(raw_id)
        if member_prof:
            existing = TrainerMemberAssignment.query.filter_by(trainer_id=profile.id, member_id=member_prof.id).first()
            if existing:
                existing.is_active = True
                existing.notes = notes
            else:
                assignment = TrainerMemberAssignment(trainer_id=profile.id, member_id=member_prof.id, notes=notes, is_active=True)
                db.session.add(assignment)
            db.session.commit()
            log_audit_event('TRAINER_ASSIGNED_CLIENT', f"Trainer {current_user.full_name} added athlete ID {member_prof.id} to roster", current_user)
            flash('Athlete added to your active training roster successfully!', 'success')
        else:
            flash('Member profile not found.', 'danger')

    return redirect(url_for('trainer.clients'))

@trainer_bp.route('/workouts', methods=['GET', 'POST'])

@trainer_bp.route('/workouts/create', methods=['POST'])
def create_workout():
    profile = get_or_create_trainer_profile()
    trainer_id = profile.id if profile else None

    raw_member_id = request.form.get('member_id', type=int)
    title = request.form.get('title', 'Hypertrophy Heavy Push/Pull/Legs Split').strip()
    goal = request.form.get('goal', 'Strength & Hypertrophy').strip()
    days_per_week = request.form.get('days_per_week', type=int) or 5
    description = request.form.get('description', '') or request.form.get('notes', '')

    if not raw_member_id:
        flash('Please select a member to assign the workout split.', 'danger')
        return redirect(url_for('trainer.workouts'))

    # Resolve member_id
    member_prof = MemberProfile.query.filter_by(user_id=raw_member_id).first() or MemberProfile.query.get(raw_member_id)
    if not member_prof:
        flash('Selected member profile not found.', 'danger')
        return redirect(url_for('trainer.workouts'))

    # Ensure TrainerMemberAssignment exists
    if trainer_id:
        existing = TrainerMemberAssignment.query.filter_by(trainer_id=trainer_id, member_id=member_prof.id).first()
        if not existing:
            assignment = TrainerMemberAssignment(trainer_id=trainer_id, member_id=member_prof.id, is_active=True)
            db.session.add(assignment)

    # Create WorkoutPlan
    plan = WorkoutPlan(
        trainer_id=trainer_id,
        member_id=member_prof.id,
        title=title,
        goal=goal,
        notes=description,
        is_active=True
    )
    db.session.add(plan)
    db.session.flush()

    # Create standard exercises
    default_exercises = [
        ("Day 1 - Push", "Barbell Bench Press", "4", "8-10", "90 sec"),
        ("Day 1 - Push", "Incline Dumbbell Press", "3", "10-12", "60 sec"),
        ("Day 2 - Pull", "Barbell Deadlift", "4", "6-8", "120 sec"),
        ("Day 2 - Pull", "Lat Pulldowns / Pull-ups", "4", "10-12", "60 sec"),
        ("Day 3 - Legs", "Barbell Back Squats", "5", "8-10", "120 sec"),
        ("Day 3 - Legs", "Leg Press / Walking Lunges", "4", "12-15", "90 sec")
    ]
    for d_name, ex_name, sets, reps, rest in default_exercises:
        w_ex = WorkoutExercise(
            workout_plan_id=plan.id,
            day_name=d_name,
            exercise_name=ex_name,
            sets=sets,
            reps=reps,
            rest_time=rest
        )
        db.session.add(w_ex)

    db.session.commit()
    log_audit_event('TRAINER_CREATED_WORKOUT', f"Workout plan '{title}' created for member ID {member_prof.id}", current_user)
    flash(f"Workout split program '{title}' assigned to athlete successfully!", 'success')
    return redirect(url_for('trainer.workouts'))

@trainer_bp.route('/workouts_view', methods=['GET'])
def workouts():
    profile = get_or_create_trainer_profile()
    trainer_id = profile.id if profile else None

    assignments = TrainerMemberAssignment.query.filter_by(trainer_id=trainer_id, is_active=True).all() if trainer_id else []
    assigned_member_ids = [a.member_id for a in assignments]

    workout_plans = WorkoutPlan.query.filter(
        (WorkoutPlan.trainer_id == trainer_id) | (WorkoutPlan.member_id.in_(assigned_member_ids))
    ).order_by(WorkoutPlan.created_at.desc()).all() if trainer_id and assigned_member_ids else (
        WorkoutPlan.query.filter_by(trainer_id=trainer_id).order_by(WorkoutPlan.created_at.desc()).all() if trainer_id else []
    )

    all_members = get_all_gym_members()
    assigned_clients = [a.member.user for a in assignments if a.member and a.member.user]

    return render_template(
        'trainer/workouts.html',
        workout_plans=workout_plans,
        clients=all_members,
        assigned_clients=assigned_clients,
        assignments=assignments
    )

@trainer_bp.route('/diets', methods=['GET', 'POST'])

@trainer_bp.route('/diets/create', methods=['POST'])
def create_diet():
    profile = get_or_create_trainer_profile()
    trainer_id = profile.id if profile else None

    raw_member_id = request.form.get('member_id', type=int)
    title = request.form.get('title', 'High Protein Diet Blueprint').strip()
    goal = request.form.get('goal', 'Lean Muscle Gain').strip()
    calories = request.form.get('target_calories', type=int) or request.form.get('daily_calories', type=int) or 2800
    protein = request.form.get('protein_grams', '180')
    if str(protein).isdigit(): protein = f"{protein}g"
    carbs = request.form.get('carbs_grams', '300')
    if str(carbs).isdigit(): carbs = f"{carbs}g"
    fats = request.form.get('fats_grams', '65')
    if str(fats).isdigit(): fats = f"{fats}g"
    description = request.form.get('description', '') or request.form.get('guidelines', '')

    if not raw_member_id:
        flash('Please select a member to assign the diet blueprint.', 'danger')
        return redirect(url_for('trainer.diets'))

    # Resolve member_id
    member_prof = MemberProfile.query.filter_by(user_id=raw_member_id).first() or MemberProfile.query.get(raw_member_id)
    if not member_prof:
        flash('Selected member profile not found.', 'danger')
        return redirect(url_for('trainer.diets'))

    # Ensure TrainerMemberAssignment exists
    if trainer_id:
        existing = TrainerMemberAssignment.query.filter_by(trainer_id=trainer_id, member_id=member_prof.id).first()
        if not existing:
            assignment = TrainerMemberAssignment(trainer_id=trainer_id, member_id=member_prof.id, is_active=True)
            db.session.add(assignment)

    # Create DietPlan
    diet = DietPlan(
        trainer_id=trainer_id,
        member_id=member_prof.id,
        title=title,
        daily_calories=calories,
        protein_grams=protein,
        carbs_grams=carbs,
        fats_grams=fats,
        guidelines=description,
        is_active=True
    )
    db.session.add(diet)
    db.session.flush()

    # Create default meals
    default_meals = [
        ("08:00 AM", "Breakfast", "6 Egg whites, 100g Rolled Oats, Banana, Black Coffee", 550, "P: 38g | C: 65g | F: 10g"),
        ("01:30 PM", "Lunch", "200g Grilled Chicken / Paneer, 150g Basmati Rice, Steamed Greens", 650, "P: 55g | C: 70g | F: 12g"),
        ("05:30 PM", "Pre-Workout Snack", "Whey Isolate Shake, Rice Cakes with Peanut Butter", 380, "P: 30g | C: 40g | F: 8g"),
        ("08:30 PM", "Dinner", "180g Salmon / Tofu, Sweet Potato, Mixed Salad", 620, "P: 45g | C: 50g | F: 18g")
    ]
    for time_str, name_str, items_str, cal_val, macro_str in default_meals:
        meal = DietMeal(
            diet_plan_id=diet.id,
            meal_time=time_str,
            meal_name=name_str,
            items=items_str,
            calories=cal_val,
            macros=macro_str
        )
        db.session.add(meal)

    db.session.commit()
    log_audit_event('TRAINER_CREATED_DIET', f"Diet plan '{title}' assigned to member ID {member_prof.id}", current_user)
    flash(f"Nutrition blueprint '{title}' assigned to athlete successfully!", 'success')
    return redirect(url_for('trainer.diets'))

@trainer_bp.route('/diets_view', methods=['GET'])
def diets():
    profile = get_or_create_trainer_profile()
    trainer_id = profile.id if profile else None

    assignments = TrainerMemberAssignment.query.filter_by(trainer_id=trainer_id, is_active=True).all() if trainer_id else []
    assigned_member_ids = [a.member_id for a in assignments]

    diet_plans = DietPlan.query.filter(
        (DietPlan.trainer_id == trainer_id) | (DietPlan.member_id.in_(assigned_member_ids))
    ).order_by(DietPlan.created_at.desc()).all() if trainer_id and assigned_member_ids else (
        DietPlan.query.filter_by(trainer_id=trainer_id).order_by(DietPlan.created_at.desc()).all() if trainer_id else []
    )

    all_members = get_all_gym_members()
    assigned_clients = [a.member.user for a in assignments if a.member and a.member.user]

    return render_template(
        'trainer/diets.html',
        diet_plans=diet_plans,
        clients=all_members,
        assigned_clients=assigned_clients,
        assignments=assignments
    )

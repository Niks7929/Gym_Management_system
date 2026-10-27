"""
SETFIT DARK RAGE - Database Seeder
Initializes database tables, creates core roles, 4 distinct membership plans in INR,
seeds the Master Admin, staff, sample members, equipment, exercises, and gym configuration.
"""
import os
from datetime import datetime, timedelta, date
from app import create_app
from app.extensions import db
from app.models.user import Role, User, MemberProfile, TrainerProfile
from app.models.membership import MembershipPlan, Membership, Payment, Enquiry
from app.models.training import Exercise, WorkoutPlan, WorkoutExercise, DietPlan, DietMeal, TrainerMemberAssignment
from app.models.operations import GymSetting, Equipment
from app.models.attendance import Attendance

app = create_app()

def seed_database():
    with app.app_context():
        print("[*] Creating all database tables...")
        db.create_all()

        # 1. Seed Roles
        print("[*] Seeding Roles (admin, trainer, member)...")
        roles = {
            'admin': 'Full administrative control and executive analytics',
            'trainer': 'Assigned athlete coaching, workout split and diet programming',
            'member': 'Gym athlete with digital biometric QR pass, workout and diet access'
        }
        role_objs = {}
        for role_name, desc in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=desc)
                db.session.add(role)
                db.session.flush()
            role_objs[role_name] = role

        # 2. Seed Gym Settings
        print("[*] Seeding Gym Settings & UPI Configuration...")
        setting = GymSetting.query.first()
        if not setting:
            setting = GymSetting(
                gym_name="SETFIT DARK RAGE",
                tagline="BUILD YOUR POWER. DEFINE YOUR LIMITS.",
                contact_phone="+91 98765 43210",
                contact_email="contact@setfitgym.com",
                address="Near Pratibha Society, Karve Nagar, Pune, Maharashtra 411052",
                upi_id="setfitdarkrage@upi",
                currency_symbol="Rs."
            )
            db.session.add(setting)

        # 3. Seed Membership Plans (Exactly 6 Unique Plans in INR)
        print("[*] Seeding 6 Canonical Membership Plans...")
        plans_data = [
            {
                'name': 'Monthly Plan',
                'price': 1600.0,
                'duration_months': 1,
                'duration_days': 30,
                'description': 'Essential monthly access for focused training routines.',
                'features': [
                    'Unlimited Gym Access',
                    'Fitness Assessment',
                    'Trainer Support',
                    'Digital Workout Dashboard'
                ]
            },
            {
                'name': 'Quarterly Plan',
                'price': 4200.0,
                'duration_months': 3,
                'duration_days': 90,
                'description': 'Quarterly commitment designed for consistent hypertrophy and strength.',
                'features': [
                    'Unlimited Gym Access',
                    'Fitness Assessment',
                    'Trainer Support',
                    'Workout & Diet Tracking'
                ]
            },
            {
                'name': 'Half-Yearly Plan',
                'price': 7000.0,
                'duration_months': 6,
                'duration_days': 180,
                'description': '6-month intensive plan including locker room and biometric scans.',
                'features': [
                    'Unlimited Gym Access',
                    'Locker Access',
                    'Trainer Support',
                    'InBody Body Scan'
                ]
            },
            {
                'name': 'Yearly Plan',
                'price': 12000.0,
                'duration_months': 12,
                'duration_days': 365,
                'description': 'Complete annual transformation package with personal training sessions.',
                'features': [
                    'Unlimited Gym Access',
                    'Fitness Assessment',
                    'Trainer Support',
                    'Workout & Diet Dashboard',
                    '2 PT Sessions'
                ]
            },
            {
                'name': 'Premium Annual VIP',
                'price': 18000.0,
                'duration_months': 12,
                'duration_days': 365,
                'description': 'Elite VIP tier with personal coach support, dedicated locker, and luxury recovery.',
                'features': [
                    'Unlimited Gym Access',
                    'Personal Trainer Support',
                    'Digital Workout & Diet Dashboard',
                    'Locker Access',
                    'Premium Facilities'
                ]
            },
            {
                'name': 'Weekend Special',
                'price': 3500.0,
                'duration_months': 3,
                'duration_days': 90,
                'description': 'Flexible access for weekend and evening powerlifters and athletes.',
                'features': [
                    'Weekend & Evening Access',
                    'Trainer Support',
                    'Digital Check-in Pass',
                    'Locker Access'
                ]
            }
        ]
        
        created_plans = {}
        for pdata in plans_data:
            plan = MembershipPlan.query.filter_by(name=pdata['name']).first()
            if not plan:
                plan = MembershipPlan(
                    name=pdata['name'],
                    price=pdata['price'],
                    duration_months=pdata['duration_months'],
                    duration_days=pdata['duration_days'],
                    description=pdata['description'],
                    is_active=True
                )
                plan.set_features(pdata['features'])
                db.session.add(plan)
                db.session.flush()
            else:
                plan.price = pdata['price']
                plan.duration_months = pdata['duration_months']
                plan.duration_days = pdata['duration_days']
                plan.description = pdata['description']
                plan.set_features(pdata['features'])
                plan.is_active = True
            created_plans[pdata['name']] = plan

        # 4. Seed Master Admin
        print("[*] Seeding Master Admin Account...")
        admin_email = "admin@setfitgym.com"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                first_name="Admin",
                last_name="",
                phone="+91 99999 88888",
                role_id=role_objs['admin'].id,
                role='admin',
                is_active=True
            )
            admin.set_password("Admin@SetFit2026!")
            db.session.add(admin)
            db.session.flush()

        # 5. Seed Equipment Inventory
        print("[*] Seeding Equipment Inventory...")
        sample_equipment = [
            ("Eleiko IPF Competition Barbell #1", "Free Weights", "EL-IPF-01", "Operational", "Racks Zone"),
            ("Eleiko IPF Competition Barbell #2", "Free Weights", "EL-IPF-02", "Operational", "Platforms"),
            ("Rogue IPF Combo Bench / Squat Rack #1", "Free Weights", "ROG-CR-01", "Operational", "Bench Row"),
            ("Hammer Strength Iso-Lateral Chest Press", "Resistance Machines", "HS-ILCP-01", "Operational", "Iso Zone"),
            ("Hammer Strength Iso-Lateral Leg Press 45 deg", "Resistance Machines", "HS-LP45-01", "Operational", "Leg Zone"),
            ("Concept2 PM5 Rower", "Cardio", "C2-ROW-01", "Operational", "Conditioning Turf"),
            ("Rogue Echo Fan Bike", "Cardio", "ROG-EB-01", "Operational", "Conditioning Turf"),
            ("Finnmark Infrared Detox Cedar Sauna Unit", "Recovery", "FM-SAUNA-01", "Operational", "Spa Wing")
        ]
        for name, cat, sn, status, loc in sample_equipment:
            if not Equipment.query.filter_by(serial_number=sn).first():
                eq = Equipment(
                    name=name,
                    category=cat,
                    serial_number=sn,
                    status=status,
                    location=loc,
                    purchase_date=date.today() - timedelta(days=90)
                )
                db.session.add(eq)

        db.session.commit()
        print("[+] SETFIT DARK RAGE Database Seeding Completed Successfully!")

if __name__ == '__main__':
    seed_database()

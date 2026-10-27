import os
import django
from datetime import time, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.branches.models import Branch, GymSetting
from apps.memberships.models import (
    MembershipPlan, Subscription, Payment, DurationType,
    SubscriptionStatus, PaymentMethod, PaymentType, PaymentStatus
)
from apps.attendance.models import Attendance, AttendanceStatus
from apps.training.models import (
    TrainerClientAssignment, WorkoutPlan, DietPlan
)

User = get_user_model()

def run_seed():
    print("[*] Initializing MySQL gym_management Database with INR currency...")

    # 1. Settings & Branches
    setting, created = GymSetting.objects.get_or_create(
        id=1,
        defaults={
            'gym_name': 'SETFIT Elite Fitness',
            'tagline': 'TRANSFORM YOUR POWER',
            'announcement_bar': '⚡ NEW ATHLETE OFFER: Sign up today & receive 1 Free Fitness Assessment + Custom Diet Plan!',
            'hero_headline': 'TRANSFORM YOUR POWER',
            'hero_subtitle': 'Welcome to SETFIT — high-performance strength and conditioning fitness facility. Master coaching, Olympic powerlifting equipment, and tailor-made nutrition plans.',
            'hero_badge_text': 'FORGED IN IRON. POWERED BY RELENTLESS DISCIPLINE.',
            'hero_cta_primary': 'Claim Membership Pass',
            'hero_cta_secondary': 'Portal Sign In',
            'contact_email': 'contact@setfitgym.com',
            'contact_phone': '+91 98765 43210',
            'address': '777 Titan Way, High Street, Mumbai',
            'currency_symbol': '₹',
            'tax_percentage': 5.0
        }
    )
    if not created:
        setting.currency_symbol = '₹'
        setting.hero_headline = 'TRANSFORM YOUR POWER'
        setting.tagline = 'TRANSFORM YOUR POWER'
        setting.save()

    b1, _ = Branch.objects.get_or_create(
        code='HQ-MUM',
        defaults={
            'name': 'SETFIT Downtown Titanium HQ',
            'address': '777 Titan Way, Bandra Kurla Complex',
            'city': 'Mumbai',
            'phone': '+91 98765 00001',
            'email': 'mumbai.hq@setfitgym.com'
        }
    )

    b2, _ = Branch.objects.get_or_create(
        code='BLR-ELITE',
        defaults={
            'name': 'SETFIT Silicon Powerhouse',
            'address': '404 Muscle Avenue, Indiranagar',
            'city': 'Bengaluru',
            'phone': '+91 98765 00002',
            'email': 'bengaluru@setfitgym.com'
        }
    )

    # 2. Membership Plans (Indian Rupees ₹)
    p_month, _ = MembershipPlan.objects.update_or_create(
        name='Iron Starter (Monthly)',
        defaults={
            'duration_type': DurationType.MONTHLY,
            'duration_days': 30,
            'price': 1499.00,
            'description': 'Full access to gym floor, locker rooms, and standard cardio equipment.',
            'features': ['24/7 Gym Floor Access', 'Locker Room & Showers', 'SETFIT Mobile Workout Logs', 'Free Water Station'],
            'is_active': True
        }
    )

    p_quarter, _ = MembershipPlan.objects.update_or_create(
        name='Titan Quarterly (3 Months)',
        defaults={
            'duration_type': DurationType.QUARTERLY,
            'duration_days': 90,
            'price': 3999.00,
            'description': 'Save 15% + 1 free fitness assessment and customized diet consultation.',
            'features': ['All Starter Features', 'Free Body Composition Scan', '1 Free Trainer Consultation', 'Sauna & Steam Bath'],
            'is_active': True
        }
    )

    p_half, _ = MembershipPlan.objects.update_or_create(
        name='Pro Athlete (6 Months)',
        defaults={
            'duration_type': DurationType.HALF_YEARLY,
            'duration_days': 180,
            'price': 6999.00,
            'description': 'Priority personal coaching booking, towel service, and guest passes.',
            'features': ['All Quarterly Features', '2 Guest Passes per Month', 'Complimentary Towel Service', 'Customized Diet Chart'],
            'is_active': True
        }
    )

    p_annual, _ = MembershipPlan.objects.update_or_create(
        name='Rage Elite VIP (Annual)',
        defaults={
            'duration_type': DurationType.YEARLY,
            'duration_days': 365,
            'price': 12999.00,
            'description': 'Ultimate all-inclusive VIP pass: All branches, unlimited sauna, personal locker, 4 personal training sessions.',
            'features': ['All-Branch Multi-Access', 'Unlimited Sauna & Hydrotherapy', 'Assigned Personal Locker', '4 1-on-1 PT Sessions', 'Monthly Fitness Audit'],
            'is_active': True
        }
    )

    # 3. Master Admin with encrypted password
    ADMIN_EMAIL = 'admin@setfitgym.com'
    ADMIN_PASSWORD = 'Admin@SetFit2026!'
    
    admin_user, _ = User.objects.get_or_create(
        email=ADMIN_EMAIL,
        defaults={
            'first_name': 'Victor',
            'last_name': 'Vance',
            'phone': '+91 98765 00000',
            'role': 'admin',
            'branch': b1,
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin_user.set_password(ADMIN_PASSWORD)
    admin_user.save()

    # Role 2: Receptionist
    rec_user, _ = User.objects.get_or_create(
        email='receptionist@setfitgym.com',
        defaults={
            'first_name': 'Pooja',
            'last_name': 'Sharma',
            'phone': '+91 98765 00010',
            'role': 'receptionist',
            'branch': b1
        }
    )
    rec_user.set_password('Recep@SetFit2026!')
    rec_user.save()

    # Role 3: Trainers
    trainer_1, _ = User.objects.get_or_create(
        email='trainer@setfitgym.com',
        defaults={
            'first_name': 'Marcus',
            'last_name': 'Titan',
            'phone': '+91 98765 00020',
            'role': 'trainer',
            'branch': b1
        }
    )
    trainer_1.set_password('Trainer@SetFit2026!')
    trainer_1.save()

    trainer_2, _ = User.objects.get_or_create(
        email='sarah.coach@setfitgym.com',
        defaults={
            'first_name': 'Sarah',
            'last_name': 'Connor',
            'phone': '+91 98765 00021',
            'role': 'trainer',
            'branch': b1
        }
    )
    trainer_2.set_password('Trainer@SetFit2026!')
    trainer_2.save()

    # Role 4: Members
    member_1, _ = User.objects.get_or_create(
        email='alex.mercer@setfitgym.com',
        defaults={
            'first_name': 'Alex',
            'last_name': 'Mercer',
            'phone': '+91 98765 00030',
            'role': 'member',
            'branch': b1
        }
    )
    member_1.set_password('Member@SetFit2026!')
    member_1.save()

    member_2, _ = User.objects.get_or_create(
        email='david.miller@example.com',
        defaults={
            'first_name': 'David',
            'last_name': 'Miller',
            'phone': '+91 98765 00031',
            'role': 'member',
            'branch': b1
        }
    )
    member_2.set_password('Member@SetFit2026!')
    member_2.save()

    # 4. Subscriptions & Payments in ₹
    today = timezone.now().date()

    sub_1, _ = Subscription.objects.get_or_create(
        member=member_1,
        plan=p_annual,
        defaults={
            'start_date': today - timedelta(days=60),
            'end_date': today + timedelta(days=305),
            'status': SubscriptionStatus.ACTIVE,
            'notes': 'VIP Member - Full Access'
        }
    )
    Payment.objects.get_or_create(
        member=member_1,
        subscription=sub_1,
        defaults={
            'amount': 12999.00,
            'payment_method': PaymentMethod.UPI,
            'payment_type': PaymentType.INITIAL,
            'status': PaymentStatus.COMPLETED,
            'transaction_date': timezone.now() - timedelta(days=60),
            'notes': 'Annual VIP package paid via UPI'
        }
    )

    # 5. Trainer Assignments
    TrainerClientAssignment.objects.get_or_create(
        trainer=trainer_1,
        member=member_1,
        defaults={'notes': 'Alex Mercer training for hypertrophy & powerlifting'}
    )

    # 6. Workout Routine
    workout_schedule = [
        {
            "day": "Day 1: Heavy Chest & Triceps (Push)",
            "exercises": [
                {"name": "Barbell Incline Bench Press", "sets": "4", "reps": "8-10", "rest": "90s", "notes": "Control tempo 3-1-0"},
                {"name": "Flat Dumbbell Press", "sets": "3", "reps": "10-12", "rest": "75s", "notes": "Deep stretch at bottom"},
                {"name": "Cable Chest Flyes", "sets": "3", "reps": "15", "rest": "60s", "notes": "Peak contraction hold 1s"},
                {"name": "Overhead Tricep Cable Extension", "sets": "4", "reps": "12", "rest": "60s", "notes": "Strict elbow position"}
            ]
        },
        {
            "day": "Day 2: Back & Biceps (Pull)",
            "exercises": [
                {"name": "Conventional Deadlift", "sets": "4", "reps": "5", "rest": "120s", "notes": "Reset each rep on floor"},
                {"name": "Chest-Supported Row", "sets": "4", "reps": "8-10", "rest": "75s", "notes": "Drive elbows back"},
                {"name": "Lat Pulldown", "sets": "3", "reps": "10-12", "rest": "60s", "notes": "Squeeze lats"},
                {"name": "Incline Dumbbell Bicep Curls", "sets": "4", "reps": "12", "rest": "60s", "notes": "Full supination"}
            ]
        },
        {
            "day": "Day 3: Quads & Hamstrings (Legs)",
            "exercises": [
                {"name": "Barbell Back Squat", "sets": "4", "reps": "6-8", "rest": "120s", "notes": "Parallel depth"},
                {"name": "Romanian Deadlift", "sets": "3", "reps": "10", "rest": "90s", "notes": "Hinge hips deep stretch"},
                {"name": "Leg Press", "sets": "3", "reps": "12-15", "rest": "75s", "notes": "Controlled tempo"}
            ]
        }
    ]

    WorkoutPlan.objects.get_or_create(
        member=member_1,
        trainer=trainer_1,
        title="Titan Hypertrophy 3-Day Split",
        defaults={
            'goal': 'Compound Strength & Hypertrophy',
            'exercises_schedule': workout_schedule,
            'start_date': today - timedelta(days=14),
            'is_active': True
        }
    )

    # 7. Diet Plan
    meals = [
        {
            "time": "08:00 AM - Breakfast",
            "meal_name": "Power Oats & Eggs",
            "items": "100g Rolled Oats, 4 Boiled Eggs, 30g Almond Butter, 1 Banana, Green Tea",
            "calories": 620,
            "protein": "42g",
            "carbs": "70g",
            "fats": "18g"
        },
        {
            "time": "01:00 PM - Lunch",
            "meal_name": "Paneer / Chicken & Brown Rice",
            "items": "200g Grilled Paneer / Chicken, 200g Brown Rice, Mixed Veg Dal & Salad",
            "calories": 700,
            "protein": "55g",
            "carbs": "65g",
            "fats": "20g"
        },
        {
            "time": "05:00 PM - Pre-Workout",
            "meal_name": "Energy Surge Snack",
            "items": "2 Slices Multigrain Toast with Peanut Butter & Banana, Black Coffee",
            "calories": 380,
            "protein": "16g",
            "carbs": "48g",
            "fats": "12g"
        },
        {
            "time": "08:30 PM - Dinner",
            "meal_name": "High-Protein Recovery Bowl",
            "items": "150g Tofu / Fish Curry, 2 Roti, Sprouts Salad, Curd",
            "calories": 650,
            "protein": "45g",
            "carbs": "55g",
            "fats": "22g"
        }
    ]

    DietPlan.objects.get_or_create(
        member=member_1,
        trainer=trainer_1,
        title="Athletic Power Diet Plan (2,600 kcal)",
        defaults={
            'daily_calories': 2600,
            'macros': {'protein': '180g', 'carbs': '280g', 'fats': '68g'},
            'meals_schedule': meals,
            'guidelines': 'Stay hydrated with at least 3.5L of water daily. Post-workout whey protein recommended within 30 minutes.',
            'is_active': True
        }
    )

    # 8. Attendance
    for day_offset in [0, 1, 2, 4, 5, 7]:
        log_date = today - timedelta(days=day_offset)
        Attendance.objects.get_or_create(
            member=member_1,
            date=log_date,
            defaults={
                'check_in_time': time(7, 30),
                'check_out_time': time(9, 0),
                'status': AttendanceStatus.PRESENT,
                'notes': 'Strength training session',
                'logged_by': rec_user
            }
        )

    print("[+] MySQL Database successfully initialized with INR currency!")
    print("--------------------------------------------------")
    print("SECRET ADMIN PORTAL ROUTE: /setfit-control-portal")
    print(f"ADMIN EMAIL:    {ADMIN_EMAIL}")
    print(f"ADMIN PASSWORD: {ADMIN_PASSWORD}")
    print("--------------------------------------------------")

if __name__ == '__main__':
    run_seed()

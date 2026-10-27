# SETFIT GYM — Enterprise Gym Management System (4-Module Architecture)

SETFIT GYM (SETFIT DARK RAGE) is a comprehensive, production-ready, full-stack fitness and gym operations platform built with **Python Flask**, **SQLAlchemy ORM**, **MySQL (WAMP/XAMPP)**, **Bootstrap 5**, **Chart.js**, and modern **Dual-Theme Dark/Light UI**.

---

## 🏛️ 4-Module Role-Based Architecture

The platform operates on a secure Role-Based Access Control (RBAC) architecture with 4 distinct modules and dedicated portal gateways:

```
                                  [ Central Gateway /portal ]
                                                │
         ┌───────────────────┬──────────────────┴──────────────────┬───────────────────┐
         ▼                   ▼                                     ▼                   ▼
  [ Master Admin ]    [ Front Desk ]                        [ Coach/Trainer ]   [ Athlete Member ]
  /admin/dashboard    /receptionist/dashboard               /trainer/dashboard  /member/dashboard
```

1. **Master Admin Module (`/admin/dashboard`)**: Central executive oversight, 6-month financial analytics, member CRUD with safe-delete cascades, trainer roster management with instant public visibility sync, membership packages, gym equipment inventory, and audit logs.
2. **Front Desk / Receptionist Module (`/receptionist/dashboard`)**: Single dedicated front-desk terminal for 24/7 biometric QR check-ins, walk-in member onboarding, membership renewals with automatic validity extension, POS cash/card billing, and enquiry lead processing.
3. **Coach / Trainer Module (`/trainer/dashboard`)**: Athlete client roster, custom multi-day workout split builder, nutrition macro & meal plan creator, and progression tracking.
4. **Athlete Member Module (`/member/dashboard`)**: Digital biometric QR pass for touchless front-desk scanning, active membership countdown, assigned workout splits, nutrition blueprints, and online UPI payment with 12-digit UTR submission.

---

## 🔐 System Logins & Credentials

| Role | Portal URL | Login Email | Password | Special Key / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Master Admin** | `/auth/admin-access` | `admin@setfitgym.com` | `Admin@SetFit2026!` | Passcode: `SETFIT_MASTER_ADMIN_PASSCODE_2026` |
| **Front Desk** | `/auth/login?role=receptionist` | `receptionist@setfitgym.com` | `Desk@2026!` | Single official front-desk account |
| **Trainer / Coach** | `/auth/login?role=trainer` | Managed by Admin | Set by Admin | E.g. `vai@gmail.com` |
| **Athlete Member** | `/auth/login?role=member` | Self-Registered / Front Desk | User-defined | E.g. `nik@gmail.com` |

---

## ⚡ Module Features Breakdown

### 1. Master Admin Module (`/admin`)
- **Executive Analytics:** Real-time metrics on total revenue, monthly intake, active members, trainer counts, and system activity.
- **Visual Analytics:** Interactive Chart.js charts showing 6-month monthly revenue trajectory and membership plan distribution.
- **Member Management:** Comprehensive search, filtering, member profile inspection, status toggling, and complete cascade safe-deletion.
- **Trainer Governance:** Coach roster management with instant toggle (`is_active`); deactivated trainers are automatically hidden from the public coaching page and hero sections.
- **Canonical Membership Plans:** 6 standardized INR pricing tiers with full feature list management.
- **Equipment Inventory:** Asset tracking with serial numbers, operational statuses, purchase dates, and gym zones.
- **Financial Controls:** Verification of member UPI UTR submissions and offline invoice audits.
- **Protected Two-Factor Gate:** Protected via master administrative passcode before session issuance.

### 2. Front Desk / Receptionist Module (`/receptionist`)
> **Note:** As specified, the front-desk operations run on **exactly 1 dedicated receptionist terminal account** (`receptionist@setfitgym.com`).
- **Front-Desk Command Terminal:** Real-time summary of today's check-ins, active memberships, 7-day expiring memberships, and daily cash intake.
- **24/7 Access & Turnstile Check-In (`/receptionist/checkin`):**
  - Biometric QR identifier / Member Code scan (`SFR-1000X`).
  - Search by name, phone number, or email.
  - Automatic session logging with check-in and check-out timestamps.
- **Walk-in Member Onboarding (`/receptionist/onboard`):**
  - Direct walk-in athlete registration.
  - Plan selection with immediate membership activation and auto-generated invoice (`INV-YYYYMMDD-XXXX`).
- **Membership Renewals (`/receptionist/renewals`):**
  - Instant filter for memberships expiring in 7 days or already expired.
  - 1-click renewal modal extending end dates seamlessly based on chosen package.
- **POS & Counter Payments (`/receptionist/payments`):**
  - POS cash and UPI billing records.
  - UTR payment verification queue with instant membership activation.
- **Enquiry & Lead Tracking (`/receptionist/enquiries`):**
  - Central queue of prospective leads submitted from the public marketing website.

### 3. Coach / Trainer Module (`/trainer`)
- **Assigned Athletes:** Dedicated directory of athletes assigned to the coach.
- **Workout Split Designer:** Creation of customized routines with targeted muscle groups, exercise selections, sets, reps, and rest intervals.
- **Diet & Nutrition Blueprints:** Daily macro allocation (Protein, Carbs, Fats) and customized meal plans.
- **Athlete Progress Tracking:** Weight, body fat, and performance monitoring.

### 4. Athlete Member Module (`/member`)
- **Digital Biometric QR Pass:** Live-rendered biometric QR pass with unique member identifier for 1-second touchless front-desk scanning.
- **Membership Passport:** Plan status, remaining active days, and expiration warnings.
- **Workout Dashboard:** Direct access to daily splits and exercise demonstration guidelines assigned by coaches.
- **Nutrition Hub:** Daily target macros and scheduled meal blueprints.
- **UPI Billing & UTR Submission:** Scan gym UPI QR code (`setfitdarkrage@upi`) and submit 12-digit transaction UTR for front-desk or admin verification.

---

## 💰 Canonical Membership Plans (INR)

| Plan Name | Duration | Price (INR) | Key Inclusions |
| :--- | :--- | :--- | :--- |
| **Monthly Plan** | 1 Month (30 Days) | **₹1,600** | Unlimited Gym Access, Fitness Assessment, Trainer Support, Digital Dashboard |
| **Weekend Special** | 3 Months (90 Days) | **₹3,500** | Weekend & Evening Access, Trainer Support, Digital Pass, Locker Access |
| **Quarterly Plan** | 3 Months (90 Days) | **₹4,200** | Unlimited Gym Access, Fitness Assessment, Trainer Support, Workout & Diet Tracking |
| **Half-Yearly Plan** | 6 Months (180 Days) | **₹7,000** | Unlimited Gym Access, Locker Access, Trainer Support, InBody Scan |
| **Yearly Plan** | 12 Months (365 Days) | **₹12,000** | Unlimited Gym Access, Assessment, Trainer Support, 2 Personal Training Sessions |
| **Premium Annual VIP**| 12 Months (365 Days) | **₹18,000** | Unlimited Access, Dedicated Coach, Locker, VIP Recovery & Spa Wing |

---

## 🛠️ Technology Stack

- **Backend Framework:** Python 3.11, Flask
- **ORM & Database:** SQLAlchemy, PyMySQL connecting to WAMP/XAMPP MySQL (`setfit_gym` at `localhost:3306`)
- **Authentication & Security:** Flask-Login, Werkzeug password hashing, multi-role RBAC decorators, CSRF protection
- **Frontend & Styling:** Bootstrap 5.3, FontAwesome 6, Chart.js, HTML5/CSS3 custom Dark Rage theme engine with instant local-storage light/dark toggle
- **Forms & Validation:** Flask-WTF, WTForms

---

## 📁 Repository Structure

```
GYM/
├── app/
│   ├── __init__.py                # App factory & Blueprint registration
│   ├── extensions.py              # db, login_manager, csrf instances
│   ├── forms/                     # WTForms form definitions
│   │   ├── admin_forms.py
│   │   ├── auth_forms.py
│   │   └── member_forms.py
│   ├── models/                    # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── attendance.py          # Attendance records
│   │   ├── membership.py          # MembershipPlan, Membership, Payment, Enquiry
│   │   ├── operations.py          # GymSetting, Equipment
│   │   ├── training.py            # WorkoutPlan, DietPlan, Exercise
│   │   └── user.py                # User, Role, MemberProfile, TrainerProfile, ReceptionistProfile
│   ├── routes/                    # Modular Blueprint controllers
│   │   ├── admin.py               # Master Admin portal routes
│   │   ├── auth.py                # Central portal & role authentication
│   │   ├── member.py              # Athlete member portal routes
│   │   ├── public.py              # Marketing landing page, plans, trainers, enquiry
│   │   ├── receptionist.py        # Front Desk / Receptionist routes
│   │   └── trainer.py             # Coach & workout/diet programming routes
│   ├── services/                  # Security RBAC & audit logging services
│   ├── static/                    # CSS, JavaScript, and branding assets
│   │   ├── css/custom.css         # Dark Rage dual-theme design tokens
│   │   └── js/app.js              # Theme engine & interactive UI components
│   └── templates/                 # Jinja2 templates grouped by role
│       ├── base.html              # Core responsive layout shell
│       ├── admin/                 # Admin dashboard, members, trainers, equipment, settings
│       ├── auth/                  # Central portal picker, login, registration, admin gate
│       ├── member/                # Member dashboard, QR pass, workout, diet, payments
│       ├── public/                # Landing page, plans, coaches, facilities
│       ├── receptionist/          # Front desk dashboard, check-in, onboarding, renewals, POS
│       └── trainer/               # Trainer dashboard, clients, workout & diet builders
├── seed_data.py                   # Canonical database initializer & seeder
├── run.py                         # Application entrypoint
├── requirements.txt               # Python package dependencies
├── test_routes.py                 # Comprehensive multi-module test suite (12 tests)
└── README.md                      # Complete system documentation
```

---

## 🚀 Setup & Execution Guide

### Prerequisites
1. **Python 3.10 or 3.11** installed.
2. **WAMP / XAMPP MySQL** running on `localhost:3306`.
3. Database `setfit_gym` created in MySQL (`CREATE DATABASE setfit_gym;`).

### 1. Clone & Install Dependencies
```bash
cd c:\Users\NIKITA\OneDrive\Desktop\project\GYM
pip install -r requirements.txt
```

### 2. Initialize Database & Seed Canonical Data
Run the database seeder to create all relational tables, 6 canonical plans, Master Admin, and the single official Front Desk account:
```bash
python seed_data.py
```

### 3. Run the Application
```bash
python run.py
```
Open your browser and navigate to:
- **Public Website & Central Portal:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Central Portal Gateway:** [http://127.0.0.1:5000/portal](http://127.0.0.1:5000/portal)
- **Front Desk Terminal:** [http://127.0.0.1:5000/receptionist/dashboard](http://127.0.0.1:5000/receptionist/dashboard)
- **Master Admin Terminal:** [http://127.0.0.1:5000/auth/admin-access](http://127.0.0.1:5000/auth/admin-access)

---

## 🧪 Automated Test Verification

A comprehensive end-to-end test suite validates all 4 modules, authentication flows, role redirects, payment verifications, and front-desk workflows.

To run the test suite:
```bash
python -m unittest test_routes.py
```

**Test Coverage Summary:**
- `test_01`: Public homepage renders marketing presentation without raw form leakage.
- `test_02`: All 6 canonical membership plans render with accurate INR pricing.
- `test_03`: Public facilities and coaching roster render properly.
- `test_04`: Central authentication gateway (`/portal`) routing and role redirects.
- `test_05`: Athlete Member login and dashboard access.
- `test_06`: Trainer / Coach login and dashboard access.
- `test_07`: **Front Desk / Receptionist login and front-desk terminal operations (Check-in, Onboard, Renewals, POS, Enquiries).**
- `test_08`: Master Admin two-factor passcode protected authentication gate.
- `test_09`: Public website enquiry lead submission.
- `test_10`: Public registration strictly assigns `member` role.
- `test_11`: Session logout and cache invalidation.
- `test_12`: End-to-end online UPI payment submission with 12-digit UTR and administrative verification.
- `test_13`: **Single Admin, Single Receptionist, Cryptographic Scrypt Password Encryption & RBAC Clearance Integrity.**
- `test_14`: **End-to-End Landing Inquiry to Receptionist Lead Desk, Admin Coach Assignment, Trainer Roster Visibility & Member Workout Synchronization Flow.**
- `test_15`: **Role-Specific Registration Isolation: Membership Plans strictly restricted to Members, Coach Specialization & Experience for Trainers, Desk Configuration for Receptionist.**

**Result: 15/15 Tests PASSED (100% OK)**

---

## 🔒 Security Best Practices Implemented
- **Strict Single Master Admin & Single Receptionist Architecture:** Database and authentication strictly enforce exactly 1 Master Admin (`admin@setfitgym.com`) and exactly 1 Front Desk Receptionist (`receptionist@setfitgym.com`). Public registration can only create `member` accounts.
- **Cryptographic Password Encryption (Scrypt):** All credentials (especially Admin and Receptionist) are hashed using modern scrypt cryptographic key derivation with high memory hardness and per-user salt. Plaintext passwords are never stored.
- **Admin Two-Factor Gate:** Admin credentials require both a secure password and master administrative passcode (`SETFIT_MASTER_ADMIN_PASSCODE_2026`).
- **Strict Role-Based Access Control (RBAC):** Users cannot access unauthorized portals; requests are intercepted by `@role_required` decorators with automatic bounce-back to their assigned terminal.
- **SQLAlchemy ORM Parameterization:** Direct protection against SQL injection attacks.
- **CSRF Token Validation:** All mutation forms (POST/PUT/DELETE) enforce cryptographic CSRF validation.

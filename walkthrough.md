# SETFIT DARK RAGE — Gym Management Platform

## 1. Architectural & Technical Overview

The **SETFIT DARK RAGE** platform is an enterprise-grade, secure Gym Management System built with Python Flask, SQLAlchemy ORM, Flask-Login, Flask-WTF with CSRF protection, and responsive Jinja2 templates (HTML5, CSS3, Bootstrap 5, Dark Rage theme with Dual Mode Dark/Light tokens, Vanilla JS, Chart.js).

---

## 2. Key Modules & Completed Deliverables

### 🚀 Public Experience & Marketing Landing Page (`/`)
- **Fix for Blank Screen Issue:** 
  - Root cause resolved: The legacy monolithic `app.py` has been replaced with the modern modular `create_app()` entrypoint.
  - Added instant CSS fallback background (`.hero-bg-slide:first-child { opacity: 1; }`) ensuring hero imagery is visible immediately even before JavaScript executes.
  - Added instant `<head>` theme initialization script to eliminate any Flash of Wrong Theme (FOWT).
  - Short non-blocking preloader (`#appPreloader`) displaying `"SMART FITNESS. STRONGER YOU."` with automatic 800ms dismissal and CSS animation fallback.
- **Dual Theme Switcher (Black / White Mode):**
  - Full design tokens implemented using CSS variables for both `:root [data-theme="dark"]` and `[data-theme="light"]`.
  - Navbar toggle button (`[ ☾ DARK ]` / `[ ☀ LIGHT ]`) with instant switching.
  - Theme preference persistence in `localStorage.getItem('setfit_theme')` with safe error-handling for private browsing modes.
- **Hero Section:**
  - Full-screen gym slideshow across 6 high-res fitness categories (modern gym interior, strength & barbells, weight training, personal coaching, cardio & ergs, professional racks).
  - Main Heading: `"TRANSFORM YOUR BODY. TRANSFORM YOUR LIFE."`
  - Subheading: `"Train smarter. Get stronger. Track your complete fitness journey."`
  - Main Buttons: `[GET STARTED]` (scrolls to `#memberships`) and `[SIGN IN TO PORTAL]` (navigates to `/portal`).
- **About SETFIT DARK RAGE:** Short, professional introduction with 4 core feature cards.
- **Why Choose Us:** 6 dedicated cards (*Professional Training, Smart Fitness Tracking, Personalized Workout, Diet Guidance, Attendance Tracking, Progress Tracking*).
- **Membership Plans (₹ INR):** Exactly 6 unique canonical tiers from the database:
  1. **Monthly Plan:** ₹1,600 / 1 Month
  2. **Weekend Special:** ₹3,500 / 3 Months
  3. **Quarterly Plan:** ₹4,200 / 3 Months
  4. **Half-Yearly Plan:** ₹7,000 / 6 Months
  5. **Yearly Plan:** ₹12,000 / 12 Months
  6. **Premium Annual VIP:** ₹18,000 / 12 Months (*VIP Tier — strictly appears ONCE*)
- **Smart Gym Management:** 8 operational capability cards.
- **Contact & Operating Hours:** Mon–Sat 5:30 AM – 11:00 PM | Sun 6:00 AM – 8:00 PM, direct phone, and clean link to `/contact`.

---

### 🔐 Central Authentication Gateway (`/portal` & `/auth/portal`)
- **Title:** `SIGN IN TO PORTAL`
- **Subtitle:** *"Choose your authorized access portal"*
- **Role Portals:** Distinct gateways for:
  - **Athlete Member** (`/member/login`)
  - **Coach / Trainer** (`/trainer/login`)
  - **Front Desk / Receptionist** (`/receptionist/login`)
- **Admin Terminal Security:** Admin is **never** a public role in dropdowns or registration. Guarded under `/auth/admin-access` requiring Master Email, Password, and secondary Master Passcode (`ADMIN_SECRET`).
- **Public Registration:** Strict enforcement of the `member` role; users cannot self-elevate permissions.

---

### 💳 Complete Membership & Payment Lifecycle
$$\text{Home / Get Started} \longrightarrow \text{Select 1 of 6 Plans} \longrightarrow \text{Register Member Account} \longrightarrow \text{Status: PENDING}$$
$$\longrightarrow \text{Member Dashboard} \longrightarrow \text{Generate UPI QR / Pay} \longrightarrow \text{Submit 12-Digit UTR} \longrightarrow \text{Admin Payment Queue}$$
$$\longrightarrow \text{Admin Verifies} \longrightarrow \text{Status: ACTIVE} \longrightarrow \text{Full Access Pass}$$

---

## 3. Automated Test Verification Results

All 12 unit and integration test suites passed with **100% Success**:

| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_01_homepage_renders_marketing_no_login_form` | Marketing home page with hero headline & no inline forms | **PASS** |
| `test_02_membership_plans_pricing_exact_six_canonical` | Exact 6 canonical INR plans with single VIP ₹18,000 instance | **PASS** |
| `test_03_facilities_and_trainers_pages` | Public facilities and coach roster rendering | **PASS** |
| `test_04_portal_selection_and_role_redirects` | Central portal gateway & direct role aliases (/portal, /member/login, etc.) | **PASS** |
| `test_05_member_login_flow` | Athlete authentication and redirect to Member Hub | **PASS** |
| `test_06_trainer_login_flow` | Coach authentication and redirect to Coach Terminal | **PASS** |
| `test_07_receptionist_login_flow` | Front desk authentication and redirect to Front Desk Terminal | **PASS** |
| `test_08_admin_security_passcode_flow` | Dual-factor admin access validation & rejection of bad passcodes | **PASS** |
| `test_09_enquiry_lead_submission` | Public assessment form submission into lead database | **PASS** |
| `test_10_member_registration_strictly_member_role` | Validation that public registration strictly creates member role | **PASS** |
| `test_11_logout_clears_session` | Complete session termination and redirect on logout | **PASS** |
| `test_12_end_to_end_payment_and_admin_verification` | Full E2E flow: Register -> Pending -> Submit UTR -> Admin Verify -> Active | **PASS** |

---

## 4. Default Seed Credentials

| Role | Email / Identifier | Password | Special Key |
| :--- | :--- | :--- | :--- |
| **Master Admin** | `admin@setfitgym.com` | `Admin@SetFit2026!` | Passcode: `SETFIT_MASTER_ADMIN_PASSCODE_2026` |
| **Head Coach** | `marcus@setfitgym.com` | `Trainer@2026!` | — |
| **Physique Coach** | `anya@setfitgym.com` | `Trainer@2026!` | — |
| **Front Desk** | `priya@setfitgym.com` | `Desk@2026!` | — |
| **Athlete Member** | `vikram@gmail.com` | `Member@2026!` | Member Code: `SFR-10001` |

---

## 5. How to Run Locally

```bash
# 1. Seed or re-seed database with canonical 6 plans
python seed_data.py

# 2. Run automated test suite
python test_routes.py

# 3. Launch application (both app.py and run.py work identically)
python run.py
```
Server runs at `http://127.0.0.1:5000`.

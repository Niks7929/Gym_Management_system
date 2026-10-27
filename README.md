# SETFIT GYM - Professional Gym Management System

A modern, responsive, and fully functional **Gym Management System** featuring complete **Master Admin** and **Receptionist Front-Desk** modules built with Python Flask, SQLite, Jinja2, Bootstrap 5, and Tailwind CSS utilities.

---

## 🚀 System Architecture & Portals

The application is structured into two dedicated management portals:

1. **Master Admin Portal (`/admin/dashboard`)**: Full administrative governance, membership packages, coaches, financial analytics, multi-category reports, and gym configurations.
2. **Receptionist Front-Desk Portal (`/receptionist/dashboard`)**: Streamlined front-desk workflows including lead capture, follow-up queues, walk-in onboarding, membership renewals, fast daily attendance, and messaging alerts.

---

## 📋 Module Overviews

### 1. Receptionist Front-Desk Module
Access URL: `http://127.0.0.1:5000/receptionist/dashboard`

- **Front-Desk Dashboard (`/receptionist/dashboard`)**:
  - Key Statistics: **New Enquiries Today**, **Follow-ups Due Today**, **Registrations This Month**, **Renewals Due Soon**, **Daily Attendance**.
  - Quick action shortcuts: Create Lead, Convert to Member, Send Message Alert, Mark Attendance.
  - Today's Follow-up Calls queue and Expiring Memberships alert box.
- **Enquiries & Lead Tracking (`/receptionist/enquiries`)**:
  - Filter by status (`New`, `Contacted`, `Converted`, `Closed`) and date.
  - Lead capture form (`/receptionist/enquiries/add`) with next follow-up date scheduling.
  - **1-Click Lead-to-Member Conversion (`/receptionist/enquiries/convert/<id>`)**: Pre-fills member details, completes registration, records payment, and automatically updates lead status.
- **Follow-ups Due (`/receptionist/followups`)**:
  - Filter by **Due Today**, **Upcoming**, **Overdue**, and **Completed**.
  - Interactive call logging modal to record prospect feedback and reschedule next call date.
- **New Registrations & Onboarding (`/receptionist/registrations`)**:
  - Onboard new gym members with automatic age calculation and auto-computed expiry dates.
- **Membership Renewals (`/receptionist/renewals`)**:
  - Track members expiring in **7 days**, **15 days**, or already expired.
  - Instant renewal modal to extend membership plan, calculate new expiry, and reactivate status.
- **Daily Attendance (`/receptionist/attendance`)**:
  - Single-click **Present** / **Absent** buttons, check-in & check-out time tracking, and workout session notes.
- **Front-Desk Messaging / SMS Alert (`/receptionist/send-sms`)**:
  - Quick communication simulation for renewal reminders, welcome alerts, and trial confirmations.

---

### 2. Master Admin Module
Access URL: `http://127.0.0.1:5000/admin/dashboard`

- **Master Admin Dashboard (`/admin/dashboard`)**:
  - Real-time statistics: Total Members, Active Memberships, Revenue Today, Revenue This Month, Total Trainers, New Enquiries.
  - Analytics widgets: 6-Month Monthly Revenue Chart, Membership Status Overview, and Plan Distribution Breakdown.
- **Members Management (`/admin/members`)**:
  - Complete CRUD, search, filter by status and plan, member profile view with attendance and payment history.
- **Membership Plans (`/admin/plans`)**:
  - Complete CRUD for packages: Monthly (₹1,500), Quarterly (₹4,000), Half-Yearly (₹7,000), and Yearly (₹12,000).
- **Trainers Management (`/admin/trainers`)**:
  - Complete coach records, specializations, experience, certifications, and profile cards.
- **Attendance & Reports (`/admin/attendance`, `/admin/reports`)**:
  - Daily gym attendance grid and multi-tab printable reports with date filters (Members, Plans, Trainers, Enquiries, Attendance, Revenue).
- **System Settings (`/admin/settings`)**:
  - Gym Profile, Admin Profile, currency symbol, date format, and operating status.

> [!NOTE]
> As specified in requirements, **Pending Dues**, **Product Sales**, and **Equipment Alerts** are strictly excluded from all views and reports.

---

## 🛠️ Technology Stack

- **Backend:** Python 3 + Flask
- **Database:** SQLite (`sqlite3`) with WAL journal mode and automatic table creation & demo data seeding
- **Frontend / Templating:** Jinja2 Template Inheritance
- **UI & Styling:**
  - Bootstrap 5 (CSS & JS CDN)
  - Tailwind CSS (CDN utility classes)
  - Bootstrap Icons CDN
  - Chart.js CDN
  - Custom Modern Dark Theme (`static/css/style.css`)

---

## 📁 Project Structure

```
GYM/
├── app.py                     # Flask entry point with all Admin and Receptionist routes
├── database.py                # SQLite schema creation & demo data seeding
├── requirements.txt           # Minimal Python dependencies (Flask)
├── README.md                  # Comprehensive documentation
│
├── templates/
│   ├── base.html              # Admin portal layout shell
│   │
│   ├── admin/                 # Admin Module templates
│   │   ├── dashboard.html
│   │   ├── members.html
│   │   ├── member_form.html
│   │   ├── member_view.html
│   │   ├── plans.html
│   │   ├── plan_form.html
│   │   ├── trainers.html
│   │   ├── trainer_form.html
│   │   ├── trainer_view.html
│   │   ├── enquiries.html
│   │   ├── enquiry_form.html
│   │   ├── enquiry_view.html
│   │   ├── attendance.html
│   │   ├── reports.html
│   │   └── settings.html
│   │
│   └── receptionist/          # Receptionist Module templates
│       ├── base.html          # Front-desk layout shell & dedicated sidebar
│       ├── dashboard.html     # Receptionist Dashboard with metrics & queue
│       ├── enquiries.html     # Lead tracking with 1-click convert
│       ├── enquiry_form.html  # Create Lead with follow-up scheduling
│       ├── followups.html     # Follow-ups due queue & call logging
│       ├── registrations.html # Member onboarding directory
│       ├── registration_form.html # Registration & lead conversion form
│       ├── renewals.html      # Expiring memberships & renewal modal
│       └── attendance.html    # Front-desk attendance marking
│
└── static/
    ├── css/
    │   └── style.css          # Modern dark gym theme styling
    └── js/
        └── main.js            # Sidebar toggle, alert dismiss, print triggers
```

---

## 💻 Installation & How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Access the Portals
- **Receptionist Portal:** [http://127.0.0.1:5000/receptionist/dashboard](http://127.0.0.1:5000/receptionist/dashboard)
- **Master Admin Portal:** [http://127.0.0.1:5000/admin/dashboard](http://127.0.0.1:5000/admin/dashboard)
- **Root URL:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 🌐 Complete Route Directory

### Receptionist Routes
| Route | Method | Description |
| :--- | :--- | :--- |
| `/receptionist` | `GET` | Redirects to `/receptionist/dashboard` |
| `/receptionist/dashboard` | `GET` | Receptionist Dashboard with front-desk stats & quick actions |
| `/receptionist/enquiries` | `GET` | View all leads, search & filter |
| `/receptionist/enquiries/add` | `GET`, `POST` | Create a new lead / enquiry |
| `/receptionist/enquiries/convert/<id>` | `GET`, `POST` | Convert prospective lead directly to active member |
| `/receptionist/followups` | `GET` | Follow-ups queue (Due Today, Upcoming, Overdue, Completed) |
| `/receptionist/followups/update/<id>` | `POST` | Log call feedback and update next follow-up date |
| `/receptionist/registrations` | `GET` | List registered members |
| `/receptionist/registrations/add` | `GET`, `POST` | Register and onboard a new member |
| `/receptionist/renewals` | `GET` | Expiring memberships queue (7 days, 15 days, expired) |
| `/receptionist/renewals/process/<id>` | `POST` | Process membership renewal and extend duration |
| `/receptionist/attendance` | `GET` | Daily attendance desk |
| `/receptionist/attendance/mark` | `POST` | Mark Present / Absent and log check-in/out times |
| `/receptionist/send-sms` | `POST` | Send front-desk message/alert simulation |
| `/receptionist/logout` | `GET` | Receptionist session logout |

### Admin Routes
| Route | Method | Description |
| :--- | :--- | :--- |
| `/admin/dashboard` | `GET` | Master Admin Dashboard |
| `/admin/members` | `GET` | Members CRUD management |
| `/admin/plans` | `GET` | Membership plans CRUD |
| `/admin/trainers` | `GET` | Trainers & coaches CRUD |
| `/admin/enquiries` | `GET` | Enquiries & status workflows |
| `/admin/attendance` | `GET` | Gym-wide attendance log |
| `/admin/reports` | `GET` | Printable multi-tab reports |
| `/admin/settings` | `GET`, `POST` | Gym information & Admin settings |

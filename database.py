import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gym.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Gym Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gym_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gym_name TEXT NOT NULL,
            gym_email TEXT,
            gym_phone TEXT,
            gym_address TEXT,
            opening_time TEXT,
            closing_time TEXT,
            admin_name TEXT,
            admin_email TEXT,
            admin_phone TEXT,
            currency_symbol TEXT DEFAULT '₹',
            date_format TEXT DEFAULT 'YYYY-MM-DD',
            gym_status TEXT DEFAULT 'Open',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Users System Table (Unified Authentication)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Membership Plans Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membership_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            duration_months INTEGER NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Trainers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            trainer_code TEXT UNIQUE,
            full_name TEXT NOT NULL,
            email TEXT,
            phone TEXT NOT NULL,
            gender TEXT,
            dob TEXT,
            specialization TEXT,
            experience_years INTEGER,
            qualification TEXT,
            joining_date TEXT NOT NULL,
            address TEXT,
            photo TEXT,
            bio TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    ''')

    # 5. Members Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            trainer_id INTEGER,
            member_code TEXT UNIQUE,
            full_name TEXT NOT NULL,
            email TEXT,
            phone TEXT NOT NULL,
            gender TEXT,
            dob TEXT,
            age INTEGER,
            address TEXT,
            emergency_contact TEXT,
            plan_id INTEGER,
            joining_date TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            photo TEXT,
            fitness_goal TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
            FOREIGN KEY (trainer_id) REFERENCES trainers (id) ON DELETE SET NULL,
            FOREIGN KEY (plan_id) REFERENCES membership_plans (id) ON DELETE SET NULL
        )
    ''')

    # Ensure missing columns exist in members & trainers table if already created
    cursor.execute("PRAGMA table_info(members)")
    m_cols = [c['name'] for c in cursor.fetchall()]
    if 'user_id' not in m_cols:
        cursor.execute("ALTER TABLE members ADD COLUMN user_id INTEGER")
    if 'trainer_id' not in m_cols:
        cursor.execute("ALTER TABLE members ADD COLUMN trainer_id INTEGER")
    if 'photo' not in m_cols:
        cursor.execute("ALTER TABLE members ADD COLUMN photo TEXT")
    if 'fitness_goal' not in m_cols:
        cursor.execute("ALTER TABLE members ADD COLUMN fitness_goal TEXT")

    cursor.execute("PRAGMA table_info(trainers)")
    t_cols = [c['name'] for c in cursor.fetchall()]
    if 'user_id' not in t_cols:
        cursor.execute("ALTER TABLE trainers ADD COLUMN user_id INTEGER")
    if 'photo' not in t_cols:
        cursor.execute("ALTER TABLE trainers ADD COLUMN photo TEXT")
    if 'bio' not in t_cols:
        cursor.execute("ALTER TABLE trainers ADD COLUMN bio TEXT")

    # 6. Enquiries Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enquiry_code TEXT UNIQUE,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            plan_id INTEGER,
            enquiry_date TEXT NOT NULL,
            source TEXT,
            message TEXT,
            status TEXT DEFAULT 'New',
            next_followup_date TEXT,
            followup_notes TEXT,
            followup_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plan_id) REFERENCES membership_plans (id) ON DELETE SET NULL
        )
    ''')

    # 7. Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            check_in TEXT,
            check_out TEXT,
            status TEXT DEFAULT 'Present',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE,
            UNIQUE(member_id, date)
        )
    ''')

    # 8. Payments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            plan_id INTEGER,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            payment_method TEXT DEFAULT 'Cash',
            status TEXT DEFAULT 'Paid',
            transaction_id TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE,
            FOREIGN KEY (plan_id) REFERENCES membership_plans (id) ON DELETE SET NULL
        )
    ''')

    cursor.execute("PRAGMA table_info(payments)")
    pay_cols = [c['name'] for c in cursor.fetchall()]
    if 'status' not in pay_cols:
        cursor.execute("ALTER TABLE payments ADD COLUMN status TEXT DEFAULT 'Paid'")
    if 'transaction_id' not in pay_cols:
        cursor.execute("ALTER TABLE payments ADD COLUMN transaction_id TEXT")

    # 9. Workout Plans Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            trainer_id INTEGER,
            workout_name TEXT NOT NULL,
            workout_type TEXT,
            exercises TEXT,
            sets INTEGER DEFAULT 3,
            reps INTEGER DEFAULT 12,
            duration TEXT,
            difficulty TEXT DEFAULT 'Intermediate',
            notes TEXT,
            start_date TEXT,
            end_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE,
            FOREIGN KEY (trainer_id) REFERENCES trainers (id) ON DELETE SET NULL
        )
    ''')

    # 10. Diet Plans Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diet_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            trainer_id INTEGER,
            meal_name TEXT NOT NULL,
            food_items TEXT NOT NULL,
            quantity TEXT,
            calories INTEGER DEFAULT 0,
            protein INTEGER DEFAULT 0,
            carbs INTEGER DEFAULT 0,
            fat INTEGER DEFAULT 0,
            timing TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE,
            FOREIGN KEY (trainer_id) REFERENCES trainers (id) ON DELETE SET NULL
        )
    ''')

    # 11. Member Progress Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS member_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            trainer_id INTEGER,
            weight REAL,
            height REAL,
            bmi REAL,
            body_fat REAL,
            chest REAL,
            waist REAL,
            arms REAL,
            thigh REAL,
            strength_level TEXT,
            fitness_goal TEXT,
            notes TEXT,
            progress_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE,
            FOREIGN KEY (trainer_id) REFERENCES trainers (id) ON DELETE SET NULL
        )
    ''')

    # 12. Trainer Notes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainer_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            trainer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            note_text TEXT NOT NULL,
            note_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE,
            FOREIGN KEY (trainer_id) REFERENCES trainers (id) ON DELETE CASCADE
        )
    ''')

    # 13. Sessions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            trainer_id INTEGER NOT NULL,
            session_date TEXT NOT NULL,
            session_time TEXT NOT NULL,
            workout_type TEXT,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE,
            FOREIGN KEY (trainer_id) REFERENCES trainers (id) ON DELETE CASCADE
        )
    ''')

    # 14. Offers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            discount_percent INTEGER DEFAULT 10,
            code TEXT UNIQUE,
            valid_from TEXT,
            valid_until TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 15. Messages Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            subject TEXT,
            message_text TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 16. Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            link TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()

    # Seed initial demo data
    seed_demo_data(cursor, conn)
    conn.close()

def seed_demo_data(cursor, conn):
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    tomorrow_str = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_str = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    two_days_ago = (today - timedelta(days=2)).strftime('%Y-%m-%d')
    five_days_ago = (today - timedelta(days=5)).strftime('%Y-%m-%d')

    # Seed Users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            ('admin', 'admin@setfitgym.com', generate_password_hash('admin123'), 'admin'),
            ('receptionist', 'receptionist@setfitgym.com', generate_password_hash('receptionist123'), 'receptionist'),
            ('trainer', 'vikram.singh@setfitgym.com', generate_password_hash('trainer123'), 'trainer'),
            ('member', 'rohan.mehta@gmail.com', generate_password_hash('member123'), 'member'),
            ('pooja_trainer', 'pooja.sharma@setfitgym.com', generate_password_hash('trainer123'), 'trainer'),
            ('rahul_trainer', 'rahul.d@setfitgym.com', generate_password_hash('trainer123'), 'trainer'),
            ('ananya_trainer', 'ananya.roy@setfitgym.com', generate_password_hash('trainer123'), 'trainer'),
            ('priya_member', 'priya.k@gmail.com', generate_password_hash('member123'), 'member'),
            ('amitabh_member', 'amitabh.v@yahoo.com', generate_password_hash('member123'), 'member'),
            ('snehal_member', 'snehal.s@gmail.com', generate_password_hash('member123'), 'member')
        ]
        cursor.executemany('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', default_users)
        conn.commit()

    # Seed Gym Settings
    cursor.execute("SELECT COUNT(*) FROM gym_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO gym_settings (
                gym_name, gym_email, gym_phone, gym_address,
                opening_time, closing_time, admin_name, admin_email,
                admin_phone, currency_symbol, date_format, gym_status
            ) VALUES (
                'SETFIT GYM', 'info@setfitgym.com', '+91 98765 43210',
                'Plot 45, Fitness Boulevard, Sector 12, Pune, Maharashtra 411001',
                '06:00 AM', '10:00 PM', 'Master Admin', 'admin@setfitgym.com',
                '+91 98765 00001', '₹', 'YYYY-MM-DD', 'Open'
            )
        ''')

    # Seed Membership Plans
    cursor.execute("SELECT COUNT(*) FROM membership_plans")
    if cursor.fetchone()[0] == 0:
        plans = [
            ('Monthly Plan', 1, 1500.0, 'Full gym access with standard cardio and weights.', 'Active'),
            ('Quarterly Plan', 3, 4000.0, '3 months access including standard diet consultation.', 'Active'),
            ('Half-Yearly Plan', 6, 7000.0, '6 months membership with locker and steam bath access.', 'Active'),
            ('Yearly Plan', 12, 12000.0, 'Annual complete package with 2 free PT sessions & full perks.', 'Active')
        ]
        cursor.executemany('''
            INSERT INTO membership_plans (name, duration_months, price, description, status)
            VALUES (?, ?, ?, ?, ?)
        ''', plans)
        conn.commit()

    # Seed Trainers
    cursor.execute("SELECT COUNT(*) FROM trainers")
    if cursor.fetchone()[0] == 0:
        trainers = [
            (3, 'TRN-101', 'Vikram Singh', 'vikram.singh@setfitgym.com', '+91 98234 11223', 'Male', '1990-05-15', 'Strength & Conditioning', 8, 'Certified Fitness Trainer (ISSA)', '2022-01-10', 'Baner, Pune', 'Active', 'Lead Coach & Bodybuilding Expert'),
            (5, 'TRN-102', 'Pooja Sharma', 'pooja.sharma@setfitgym.com', '+91 98234 22334', 'Female', '1994-08-22', 'Yoga & Functional Mobility', 5, 'Master in Physical Education & Yoga Certified', '2022-06-01', 'Kothrud, Pune', 'Active', 'Specialist in flexibility and holistic wellness'),
            (6, 'TRN-103', 'Rahul Deshmukh', 'rahul.d@setfitgym.com', '+91 98234 33445', 'Male', '1992-11-03', 'CrossFit & Calisthenics', 6, 'CrossFit Level 2 Trainer', '2023-02-15', 'Wakad, Pune', 'Active', 'High-intensity functional movement trainer'),
            (7, 'TRN-104', 'Ananya Roy', 'ananya.roy@setfitgym.com', '+91 98234 44556', 'Female', '1996-03-19', 'Cardio & HIIT Specialist', 4, 'ACE Certified Personal Trainer', '2023-08-01', 'Viman Nagar, Pune', 'Active', 'Weight loss & endurance coach'),
            (None, 'TRN-105', 'Sameer Khan', 'sameer.khan@setfitgym.com', '+91 98234 55667', 'Male', '1989-12-10', 'Bodybuilding & Nutrition', 10, 'K11 Academy of Fitness Sciences Diploma', '2021-03-12', 'Aundh, Pune', 'Active', 'Hypertrophy & contest prep master'),
            (None, 'TRN-106', 'Sneha Patil', 'sneha.patil@setfitgym.com', '+91 98234 66778', 'Female', '1995-07-28', 'Pilates & Core Training', 4, 'Comprehensive Pilates Instructor (PMA)', '2024-01-05', 'Hinjewadi, Pune', 'Active', 'Core stability & posture specialist')
        ]
        cursor.executemany('''
            INSERT INTO trainers (
                user_id, trainer_code, full_name, email, phone, gender, dob,
                specialization, experience_years, qualification, joining_date, address, status, bio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', trainers)
        conn.commit()
    else:
        # Link user_id to trainers if not set
        cursor.execute("UPDATE trainers SET user_id = 3 WHERE id = 1 AND (user_id IS NULL OR user_id = 0)")
        cursor.execute("UPDATE trainers SET user_id = 5 WHERE id = 2 AND (user_id IS NULL OR user_id = 0)")
        cursor.execute("UPDATE trainers SET user_id = 6 WHERE id = 3 AND (user_id IS NULL OR user_id = 0)")
        cursor.execute("UPDATE trainers SET user_id = 7 WHERE id = 4 AND (user_id IS NULL OR user_id = 0)")
        conn.commit()

    # Seed Members
    cursor.execute("SELECT COUNT(*) FROM members")
    if cursor.fetchone()[0] == 0:
        members_data = [
            (4, 1, 'MEM-1001', 'Rohan Mehta', 'rohan.mehta@gmail.com', '+91 98111 00001', 'Male', '1998-04-12', 28, 'Model Colony, Pune', '+91 98111 99991', 4, (today - timedelta(days=120)).strftime('%Y-%m-%d'), (today - timedelta(days=120)).strftime('%Y-%m-%d'), (today + timedelta(days=245)).strftime('%Y-%m-%d'), 'Active', 'Muscle gain & strength conditioning'),
            (8, 2, 'MEM-1002', 'Priya Kulkarni', 'priya.k@gmail.com', '+91 98111 00002', 'Female', '2001-09-20', 25, 'Kothrud, Pune', '+91 98111 99992', 2, (today - timedelta(days=40)).strftime('%Y-%m-%d'), (today - timedelta(days=40)).strftime('%Y-%m-%d'), (today + timedelta(days=50)).strftime('%Y-%m-%d'), 'Active', 'Weight loss & posture improvement'),
            (9, 1, 'MEM-1003', 'Amitabh Verma', 'amitabh.v@yahoo.com', '+91 98111 00003', 'Male', '1987-02-18', 39, 'Kalyani Nagar, Pune', '+91 98111 99993', 3, (today - timedelta(days=80)).strftime('%Y-%m-%d'), (today - timedelta(days=80)).strftime('%Y-%m-%d'), (today + timedelta(days=100)).strftime('%Y-%m-%d'), 'Active', 'Body recomposition & stamina'),
            (10, 4, 'MEM-1004', 'Snehal Shinde', 'snehal.s@gmail.com', '+91 98111 00004', 'Female', '1995-12-05', 30, 'Baner, Pune', '+91 98111 99994', 1, (today - timedelta(days=15)).strftime('%Y-%m-%d'), (today - timedelta(days=15)).strftime('%Y-%m-%d'), (today + timedelta(days=15)).strftime('%Y-%m-%d'), 'Active', 'HIIT cardio & endurance'),
            (None, 1, 'MEM-1005', 'Karan Johar', 'karan.j@outlook.com', '+91 98111 00005', 'Male', '1993-06-30', 33, 'Shivaji Nagar, Pune', '+91 98111 99995', 4, (today - timedelta(days=200)).strftime('%Y-%m-%d'), (today - timedelta(days=200)).strftime('%Y-%m-%d'), (today + timedelta(days=165)).strftime('%Y-%m-%d'), 'Active', 'Lean muscle building'),
            (None, 2, 'MEM-1006', 'Neha Rajput', 'neha.rajput@gmail.com', '+91 98111 00006', 'Female', '2000-01-14', 26, 'Hadapsar, Pune', '+91 98111 99996', 2, (today - timedelta(days=110)).strftime('%Y-%m-%d'), (today - timedelta(days=110)).strftime('%Y-%m-%d'), (today - timedelta(days=20)).strftime('%Y-%m-%d'), 'Expired', 'Weight loss'),
            (None, 3, 'MEM-1007', 'Aditya Joshi', 'aditya.joshi@gmail.com', '+91 98111 00007', 'Male', '1996-10-08', 29, 'Aundh, Pune', '+91 98111 99997', 1, (today - timedelta(days=45)).strftime('%Y-%m-%d'), (today - timedelta(days=45)).strftime('%Y-%m-%d'), (today - timedelta(days=15)).strftime('%Y-%m-%d'), 'Expired', 'General fitness'),
            (None, 2, 'MEM-1008', 'Tanvi Mahajan', 'tanvi.m@gmail.com', '+91 98111 00008', 'Female', '1999-07-22', 27, 'Pashan, Pune', '+91 98111 99998', 3, (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today + timedelta(days=175)).strftime('%Y-%m-%d'), 'Active', 'Tone & flexibility'),
            (None, 1, 'MEM-1009', 'Nitin Gadre', 'nitin.gadre@gmail.com', '+91 98111 00009', 'Male', '1985-03-11', 41, 'Camp, Pune', '+91 98111 99999', 4, (today - timedelta(days=350)).strftime('%Y-%m-%d'), (today - timedelta(days=350)).strftime('%Y-%m-%d'), (today + timedelta(days=15)).strftime('%Y-%m-%d'), 'Active', 'Cardiovascular health'),
            (None, 4, 'MEM-1010', 'Deepika Nair', 'deepika.nair@gmail.com', '+91 98111 00010', 'Female', '1997-11-25', 28, 'Wakad, Pune', '+91 98111 99990', 2, (today - timedelta(days=30)).strftime('%Y-%m-%d'), (today - timedelta(days=30)).strftime('%Y-%m-%d'), (today + timedelta(days=60)).strftime('%Y-%m-%d'), 'Inactive', 'Fat loss')
        ]
        cursor.executemany('''
            INSERT INTO members (
                user_id, trainer_id, member_code, full_name, email, phone, gender, dob, age,
                address, emergency_contact, plan_id, joining_date, start_date,
                end_date, status, fitness_goal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', members_data)
        conn.commit()

        # Seed Payments
        payments_data = [
            (1, 4, 12000.0, (today - timedelta(days=120)).strftime('%Y-%m-%d'), 'UPI', 'Paid', 'TXN10001', 'Annual subscription'),
            (2, 2, 4000.0, (today - timedelta(days=40)).strftime('%Y-%m-%d'), 'Credit Card', 'Paid', 'TXN10002', 'Quarterly subscription'),
            (3, 3, 7000.0, (today - timedelta(days=80)).strftime('%Y-%m-%d'), 'Net Banking', 'Paid', 'TXN10003', 'Half-yearly plan'),
            (4, 1, 1500.0, (today - timedelta(days=15)).strftime('%Y-%m-%d'), 'Cash', 'Paid', 'TXN10004', 'Monthly membership'),
            (5, 4, 12000.0, (today - timedelta(days=200)).strftime('%Y-%m-%d'), 'UPI', 'Paid', 'TXN10005', 'Annual plan'),
            (6, 2, 4000.0, (today - timedelta(days=110)).strftime('%Y-%m-%d'), 'Cash', 'Paid', 'TXN10006', 'Previous quarterly plan'),
            (7, 1, 1500.0, (today - timedelta(days=45)).strftime('%Y-%m-%d'), 'UPI', 'Paid', 'TXN10007', 'Previous monthly plan'),
            (8, 3, 7000.0, (today - timedelta(days=5)).strftime('%Y-%m-%d'), 'UPI', 'Paid', 'TXN10008', 'Half-yearly plan'),
            (9, 4, 12000.0, (today - timedelta(days=350)).strftime('%Y-%m-%d'), 'Debit Card', 'Paid', 'TXN10009', 'Annual plan'),
            (10, 2, 4000.0, (today - timedelta(days=30)).strftime('%Y-%m-%d'), 'UPI', 'Paid', 'TXN10010', 'Quarterly plan'),
            (1, 1, 1500.0, today.strftime('%Y-%m-%d'), 'UPI', 'Pending', 'TXN-REQ-101', 'Personal trainer monthly addon fee')
        ]
        cursor.executemany('''
            INSERT INTO payments (member_id, plan_id, amount, payment_date, payment_method, status, transaction_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', payments_data)
        conn.commit()
    else:
        # Link user_id & trainer_id to members if missing
        cursor.execute("UPDATE members SET user_id = 4, trainer_id = 1 WHERE id = 1 AND (user_id IS NULL OR user_id = 0)")
        cursor.execute("UPDATE members SET user_id = 8, trainer_id = 2 WHERE id = 2 AND (user_id IS NULL OR user_id = 0)")
        cursor.execute("UPDATE members SET user_id = 9, trainer_id = 1 WHERE id = 3 AND (user_id IS NULL OR user_id = 0)")
        cursor.execute("UPDATE members SET user_id = 10, trainer_id = 4 WHERE id = 4 AND (user_id IS NULL OR user_id = 0)")
        cursor.execute("UPDATE members SET trainer_id = 1 WHERE trainer_id IS NULL")
        conn.commit()

    # Seed Workout Plans
    cursor.execute("SELECT COUNT(*) FROM workout_plans")
    if cursor.fetchone()[0] == 0:
        workouts_data = [
            (1, 1, 'Hypertrophy Upper Body Power', 'Strength & Hypertrophy', 'Bench Press, Barbell Rows, Overhead Press, Incline Dumbbell Press, Bicep Curls', 4, 10, '60 mins', 'Intermediate', 'Focus on progressive overload and strict form.', today_str, (today + timedelta(days=30)).strftime('%Y-%m-%d')),
            (1, 1, 'Lower Body Core Blast', 'Legs & Abs', 'Barbell Squats, Romanian Deadlifts, Leg Press, Calf Raises, Hanging Leg Raises', 4, 12, '50 mins', 'Advanced', 'Stay hydrated and stretch thoroughly after session.', today_str, (today + timedelta(days=30)).strftime('%Y-%m-%d')),
            (2, 2, 'Core & Functional Mobility Routine', 'Yoga & Pilates', 'Sun Salutations, Plank Hold, Bird Dog, Warrior Poses, Glute Bridges', 3, 15, '45 mins', 'Beginner', 'Focus on deep nasal breathing and core engagement.', today_str, (today + timedelta(days=30)).strftime('%Y-%m-%d')),
            (3, 1, 'Heavy Compound Strength Circuit', 'Powerlifting', 'Deadlifts, Bench Press, Back Squats, Weighted Dips', 5, 5, '70 mins', 'Advanced', 'Rest 2-3 mins between heavy sets.', today_str, (today + timedelta(days=30)).strftime('%Y-%m-%d')),
            (4, 4, 'High Intensity Fat Burner', 'HIIT & Cardio', 'Treadmill Sprints, Kettlebell Swings, Burpees, Mountain Climbers, Jump Rope', 4, 20, '40 mins', 'Intermediate', 'Keep heart rate in 75-85% max zone.', today_str, (today + timedelta(days=30)).strftime('%Y-%m-%d'))
        ]
        cursor.executemany('''
            INSERT INTO workout_plans (member_id, trainer_id, workout_name, workout_type, exercises, sets, reps, duration, difficulty, notes, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', workouts_data)
        conn.commit()

    # Seed Diet Plans
    cursor.execute("SELECT COUNT(*) FROM diet_plans")
    if cursor.fetchone()[0] == 0:
        diets_data = [
            (1, 1, 'Breakfast', '4 Egg Whites + 2 Whole Eggs, 1 Bowl Oats with Almonds & Banana', '2 Bowls', 550, 35, 60, 15, '07:30 AM', 'High protein start for morning workout energy.'),
            (1, 1, 'Lunch', '200g Grilled Chicken Breast, 1.5 Cup Brown Rice, Steamed Broccoli & Salad', '1 Plate', 650, 45, 70, 12, '01:30 PM', 'Drink 500ml water 30 mins before lunch.'),
            (1, 1, 'Evening Snack', '1 Scoop Whey Protein Isolate with Water, 1 Apple, Handful Walnuts', '1 Serving', 280, 26, 25, 8, '05:30 PM', 'Pre-workout booster.'),
            (1, 1, 'Dinner', '150g Paneer Tofu / Fish Curry, 2 Multigrain Rotis, Cucumber Tomato Salad', '1 Plate', 500, 30, 40, 18, '09:00 PM', 'Light dinner before sleep.'),
            (2, 2, 'Breakfast', 'Green Smoothie (Spinach, Chia Seeds, Banana, Whey), 2 Boiled Eggs', '1 Glass', 380, 22, 45, 8, '08:00 AM', 'Detox and weight loss morning blend.'),
            (2, 2, 'Lunch', 'Dal Tadka, 1 Bowl Quinoa / Brown Rice, Mixed Veg Sabzi', '1 Bowl', 420, 18, 65, 10, '01:00 PM', 'High fiber plant-based lunch.'),
            (3, 1, 'High-Calorie Muscle Builder', 'Oatmeal with Peanut Butter & Whey, 4 Whole Eggs, 300g Rice with Chicken', 'Daily Full', 2800, 160, 320, 70, 'All Day', 'Consistently hit protein targets for hypertrophy.')
        ]
        cursor.executemany('''
            INSERT INTO diet_plans (member_id, trainer_id, meal_name, food_items, quantity, calories, protein, carbs, fat, timing, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', diets_data)
        conn.commit()

    # Seed Member Progress
    cursor.execute("SELECT COUNT(*) FROM member_progress")
    if cursor.fetchone()[0] == 0:
        progress_data = [
            (1, 1, 78.5, 178.0, 24.8, 18.5, 41.0, 32.5, 14.5, 23.0, 'Advanced', 'Muscle Gain', 'Gained 2.5kg muscle mass, chest expanded by 1.5 inches.', (today - timedelta(days=90)).strftime('%Y-%m-%d')),
            (1, 1, 80.2, 178.0, 25.3, 17.2, 42.2, 32.0, 15.0, 23.5, 'Advanced', 'Muscle Gain', 'Strength improved on bench press (100kg x 5).', (today - timedelta(days=45)).strftime('%Y-%m-%d')),
            (1, 1, 81.5, 178.0, 25.7, 16.5, 43.0, 31.8, 15.5, 24.0, 'Advanced', 'Muscle Gain', 'Peak peak condition achieved. Great symmetry.', today_str),
            (2, 2, 68.0, 165.0, 25.0, 28.0, 36.0, 31.0, 11.5, 21.0, 'Intermediate', 'Weight Loss', 'Initial assessment.', (today - timedelta(days=40)).strftime('%Y-%m-%d')),
            (2, 2, 64.5, 165.0, 23.7, 24.5, 35.0, 28.5, 11.0, 20.2, 'Intermediate', 'Weight Loss', 'Lost 3.5kg fat! Inches dropped around waist.', today_str)
        ]
        cursor.executemany('''
            INSERT INTO member_progress (member_id, trainer_id, weight, height, bmi, body_fat, chest, waist, arms, thigh, strength_level, fitness_goal, notes, progress_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', progress_data)
        conn.commit()

    # Seed Trainer Notes
    cursor.execute("SELECT COUNT(*) FROM trainer_notes")
    if cursor.fetchone()[0] == 0:
        notes_data = [
            (1, 1, 'Form Check on Heavy Squats', 'Rohan is lifting 120kg squats cleanly. Ensure lower back remains tight on final set.', today_str),
            (1, 1, 'Nutritional Adjustment', 'Increased daily carbohydrate intake by 50g on leg training days.', yesterday_str),
            (2, 2, 'Yoga Flexibility Improvement', 'Priya completed 45 mins full vinyasa flow with improved hamstring range.', today_str)
        ]
        cursor.executemany('''
            INSERT INTO trainer_notes (member_id, trainer_id, title, note_text, note_date)
            VALUES (?, ?, ?, ?, ?)
        ''', notes_data)
        conn.commit()

    # Seed Sessions
    cursor.execute("SELECT COUNT(*) FROM sessions")
    if cursor.fetchone()[0] == 0:
        sessions_data = [
            (1, 1, today_str, '07:00 AM', 'Strength & Hypertrophy', 'In Progress', 'Focusing on upper body push day.'),
            (3, 1, today_str, '08:30 AM', 'Heavy Compound Strength', 'Scheduled', 'Deadlift max testing.'),
            (2, 2, today_str, '09:30 AM', 'Core & Mobility', 'Completed', 'Priya completed full 45 min mobility routine.'),
            (4, 4, today_str, '05:00 PM', 'HIIT Cardio Burner', 'Scheduled', 'Evening conditioning session.'),
            (1, 1, yesterday_str, '07:00 AM', 'Legs & Abs', 'Completed', 'Pushed through 5 heavy squat sets.')
        ]
        cursor.executemany('''
            INSERT INTO sessions (member_id, trainer_id, session_date, session_time, workout_type, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sessions_data)
        conn.commit()

    # Seed Offers
    cursor.execute("SELECT COUNT(*) FROM offers")
    if cursor.fetchone()[0] == 0:
        offers_data = [
            ('Monsoon Fitness Blast', 'Get flat 20% discount on all 6-month & 1-year annual memberships.', 20, 'MONSOON20', (today - timedelta(days=10)).strftime('%Y-%m-%d'), (today + timedelta(days=30)).strftime('%Y-%m-%d'), 'Active'),
            ('Personal Training Duo Offer', 'Book 3 months of Personal Training and get 1 month of custom Diet Consultation FREE!', 15, 'PTDUO15', (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today + timedelta(days=45)).strftime('%Y-%m-%d'), 'Active'),
            ('Student Special Pass', 'Flat ₹500 instant off for college students on monthly passes.', 10, 'STUDENT500', today_str, (today + timedelta(days=60)).strftime('%Y-%m-%d'), 'Active')
        ]
        cursor.executemany('''
            INSERT INTO offers (title, description, discount_percent, code, valid_from, valid_until, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', offers_data)
        conn.commit()

    # Seed Messages
    cursor.execute("SELECT COUNT(*) FROM messages")
    if cursor.fetchone()[0] == 0:
        messages_data = [
            (4, 3, 'Workout Query', 'Hi Coach Vikram, should I increase my bench press weight tomorrow?', 1, (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')),
            (3, 4, 'RE: Workout Query', 'Yes Rohan, add 2.5kg on each side. Keep a spotter nearby for the 4th set!', 1, (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')),
            (4, 1, 'Locker Access Inquiry', 'Hello Admin, can I request a permanent locker assignment for morning slots?', 0, today_str + ' 08:30:00')
        ]
        cursor.executemany('''
            INSERT INTO messages (sender_id, receiver_id, subject, message_text, is_read, sent_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', messages_data)
        conn.commit()

    # Enquiries & Attendance verification
    cursor.execute("SELECT COUNT(*) FROM enquiries")
    if cursor.fetchone()[0] == 0:
        enquiries_data = [
            ('ENQ-501', 'Rahul Sharma', '+91 99887 11223', 'rahul.s@gmail.com', 4, today_str, 'Instagram', 'Interested in annual membership and evening batch timing.', 'New', today_str, 'Call regarding 10% annual discount offer', 'Pending'),
            ('ENQ-502', 'Meera Rao', '+91 99887 22334', 'meera.rao@outlook.com', 2, today_str, 'Google Search', 'Looking for female trainer availability and weight loss regime.', 'New', today_str, 'Schedule demo trial session with Pooja', 'Pending'),
            ('ENQ-503', 'Kunal Ghosh', '+91 99887 33445', 'kunal.g@gmail.com', 1, yesterday_str, 'Walk-in', 'Walked in to check facilities and dumbbell sets.', 'Contacted', tomorrow_str, 'Follow up after facility walkthrough', 'Scheduled'),
            ('ENQ-504', 'Divya Sen', '+91 99887 44556', 'divya.sen@gmail.com', 3, two_days_ago, 'Referral', 'Friend referred for half-yearly yoga & cardio combo.', 'Converted', yesterday_str, 'Converted to active member', 'Completed'),
            ('ENQ-505', 'Prateek Jain', '+91 99887 55667', 'prateek.jain@gmail.com', 4, five_days_ago, 'Facebook', 'Inquired about corporate discounts for team of 5.', 'Closed', two_days_ago, 'Not interested at this time', 'Completed')
        ]
        cursor.executemany('''
            INSERT INTO enquiries (enquiry_code, full_name, phone, email, plan_id, enquiry_date, source, message, status, next_followup_date, followup_notes, followup_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', enquiries_data)
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM attendance")
    if cursor.fetchone()[0] == 0:
        attendance_data = [
            (1, today_str, '06:30 AM', '08:00 AM', 'Present', 'Morning workout'),
            (2, today_str, '07:15 AM', '08:45 AM', 'Present', 'Cardio & stretching'),
            (3, today_str, '08:00 AM', '09:30 AM', 'Present', 'Chest & Triceps'),
            (4, today_str, None, None, 'Absent', 'No show'),
            (5, today_str, '06:00 PM', None, 'Present', 'Evening batch check-in'),
            (8, today_str, '07:00 AM', '08:15 AM', 'Present', 'HIIT session'),
            (1, yesterday_str, '06:45 AM', '08:15 AM', 'Present', 'Leg day'),
            (2, yesterday_str, '07:30 AM', '09:00 AM', 'Present', 'Yoga workout'),
            (3, yesterday_str, '08:15 AM', '09:45 AM', 'Present', 'Back & Biceps')
        ]
        cursor.executemany('''
            INSERT INTO attendance (member_id, date, check_in, check_out, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', attendance_data)
        conn.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized and full multi-role demo data seeded successfully!")

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# We will import db from app extensions
from app.extensions import db

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # 'admin', 'trainer', 'receptionist', 'member'
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='user_role', lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='member') # cached string for fast RBAC
    
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blocked = db.Column(db.Boolean, default=False, nullable=False)
    
    # Security parameters
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    member_profile = db.relationship('MemberProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    trainer_profile = db.relationship('TrainerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='actor', lazy='dynamic')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    @full_name.setter
    def full_name(self, value):
        if value:
            parts = value.strip().split(' ', 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else ''
        else:
            self.first_name = ''
            self.last_name = ''

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.locked_until = None

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

class MemberProfile(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True) # Male, Female, Other
    emergency_contact = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    fitness_goal = db.Column(db.String(100), nullable=True) # Hypertrophy, Fat Loss, Powerlifting, General Fitness
    medical_conditions = db.Column(db.Text, nullable=True)
    
    join_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='member', lazy=True, cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='member', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='member', lazy=True, cascade='all, delete-orphan')
    trainer_assignments = db.relationship('TrainerMemberAssignment', backref='member', lazy=True)
    workout_plans = db.relationship('WorkoutPlan', backref='member', lazy=True)
    diet_plans = db.relationship('DietPlan', backref='member', lazy=True)

    @property
    def member_code(self):
        return f"SFR-{self.id + 10000}" if self.id else "SFR-MEMBER"

    @property
    def active_membership(self):
        now = datetime.utcnow().date()
        for m in self.memberships:
            if m.status == 'active' and m.start_date <= now <= m.end_date:
                return m
        return None

    @property
    def full_name(self):
        return self.user.full_name if self.user else ""

    @property
    def email(self):
        return self.user.email if self.user else ""

    @property
    def phone(self):
        return self.user.phone if self.user else ""

    @property
    def is_active(self):
        return self.user.is_active if self.user else True

    @property
    def is_blocked(self):
        return self.user.is_blocked if self.user else False

    def __repr__(self):
        return f"<MemberProfile {self.user.email if self.user else self.id}>"

class TrainerProfile(db.Model):
    __tablename__ = 'trainers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    specialization = db.Column(db.String(120), nullable=True) # Strength & Conditioning, Powerlifting, Nutrition
    experience_years = db.Column(db.Integer, default=1)
    certifications = db.Column(db.Text, nullable=True)
    hourly_rate = db.Column(db.Float, default=500.0) # in INR (₹)
    bio = db.Column(db.Text, nullable=True)
    
    # Relationships
    assigned_members = db.relationship('TrainerMemberAssignment', backref='trainer', lazy=True)
    created_workouts = db.relationship('WorkoutPlan', backref='trainer', lazy=True)
    created_diets = db.relationship('DietPlan', backref='trainer', lazy=True)

    @property
    def full_name(self):
        return self.user.full_name if self.user else ""

    @property
    def email(self):
        return self.user.email if self.user else ""

    @property
    def phone(self):
        return self.user.phone if self.user else ""

    @property
    def is_active(self):
        return self.user.is_active if self.user else True

    @property
    def is_blocked(self):
        return self.user.is_blocked if self.user else False

    def __repr__(self):
        return f"<TrainerProfile {self.user.email if self.user else self.id}>"



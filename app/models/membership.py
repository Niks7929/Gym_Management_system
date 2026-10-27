from datetime import datetime, date, timedelta
import json
from app.extensions import db

class MembershipPlan(db.Model):
    __tablename__ = 'membership_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # e.g., BASIC, STANDARD, PREMIUM, ELITE
    duration_months = db.Column(db.Integer, default=1)
    duration_days = db.Column(db.Integer, default=30)
    price = db.Column(db.Float, nullable=False) # in Indian Rupees (₹)
    description = db.Column(db.Text, nullable=True)
    features_json = db.Column(db.Text, nullable=True) # JSON array string of features
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    memberships = db.relationship('Membership', backref='plan', lazy=True)

    @property
    def features_list(self):
        if self.features_json:
            try:
                return json.loads(self.features_json)
            except Exception:
                return [f.strip() for f in self.features_json.split(',') if f.strip()]
        return []

    def set_features(self, features_list):
        self.features_json = json.dumps(features_list)

    def __repr__(self):
        return f"<MembershipPlan {self.name} - ₹{self.price}>"

class Membership(db.Model):
    __tablename__ = 'memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('membership_plans.id'), nullable=False)
    
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default='active', nullable=False) # 'active', 'pending_verification', 'expired', 'cancelled'
    
    amount_paid = db.Column(db.Float, nullable=False, default=0.0)
    is_verified = db.Column(db.Boolean, default=True, nullable=False)
    utr_number = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payments = db.relationship('Payment', backref='membership', lazy=True)

    @property
    def is_currently_active(self):
        today = date.today()
        return self.status == 'active' and self.start_date <= today <= self.end_date

    @property
    def days_remaining(self):
        today = date.today()
        if self.end_date < today:
            return 0
        return (self.end_date - today).days

    def __repr__(self):
        return f"<Membership Member:{self.member_id} Plan:{self.plan_id} Status:{self.status}>"

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('memberships.id', ondelete='SET NULL'), nullable=True)
    
    amount = db.Column(db.Float, nullable=False) # in ₹ INR
    payment_method = db.Column(db.String(30), default='upi') # 'cash', 'card', 'upi', 'bank_transfer'
    payment_type = db.Column(db.String(30), default='initial') # 'initial', 'renewal', 'addon', 'product'
    status = db.Column(db.String(30), default='completed') # 'completed', 'pending_verification', 'rejected', 'failed'
    
    utr_number = db.Column(db.String(100), nullable=True)
    upi_vpa = db.Column(db.String(100), nullable=True)
    rejection_reason = db.Column(db.String(255), nullable=True)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    verified_by = db.relationship('User', foreign_keys=[verified_by_id])

    @property
    def receipt_number(self):
        return self.invoice_number

    @property
    def payment_status(self):
        return self.status

    @property
    def payment_date(self):
        return self.transaction_date

    @property
    def user(self):
        return self.member.user if self.member else None

    @property
    def transaction_id(self):
        return self.utr_number

    def __repr__(self):
        return f"<Payment {self.invoice_number} - ₹{self.amount} ({self.status})>"

class Enquiry(db.Model):
    __tablename__ = 'enquiries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    preferred_branch = db.Column(db.String(100), nullable=True)
    fitness_goal = db.Column(db.String(100), nullable=True)
    preferred_time = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(30), default='new', nullable=False) # 'new', 'contacted', 'converted', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def full_name(self):
        return self.name

    @property
    def interested_program(self):
        return self.fitness_goal

    @property
    def message(self):
        return self.notes

    def __repr__(self):
        return f"<Enquiry {self.name} - {self.phone} ({self.status})>"


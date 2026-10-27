from datetime import datetime, timedelta
import secrets
from app.extensions import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user_email = db.Column(db.String(120), nullable=True)
    user_role = db.Column(db.String(50), nullable=True)
    
    action = db.Column(db.String(100), nullable=False) # e.g., 'LOGIN_SUCCESS', 'FAILED_LOGIN', 'MEMBER_CREATED', 'PAYMENT_VERIFIED'
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    @property
    def created_at(self):
        return self.timestamp

    @property
    def user(self):
        return self.actor

    @property
    def severity(self):
        act = (self.action or '').upper()
        if 'FAILED' in act or 'DELETE' in act or 'REJECT' in act or 'LOCK' in act:
            return 'high'
        elif 'UPDATE' in act or 'TOGGLE' in act or 'CREATE' in act:
            return 'warning'
        return 'info'

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_email or 'Anonymous'} at {self.timestamp}>"

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='password_resets')

    @classmethod
    def generate_token(cls, user_id, valid_hours=2):
        return cls(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(hours=valid_hours)
        )

    def is_valid(self):
        return not self.used and self.expires_at > datetime.utcnow()

    def __repr__(self):
        return f"<PasswordReset User:{self.user_id} Token:{self.token[:8]}...>"

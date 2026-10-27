from datetime import datetime, date, time
from app.extensions import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    
    date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    check_in_time = db.Column(db.Time, default=lambda: datetime.now().time(), nullable=False)
    check_out_time = db.Column(db.Time, nullable=True)
    
    status = db.Column(db.String(20), default='present', nullable=False) # 'present', 'late', 'absent'
    notes = db.Column(db.String(255), nullable=True)
    logged_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    logged_by = db.relationship('User', foreign_keys=[logged_by_id])

    @property
    def user(self):
        return self.member.user if self.member else None

    @property
    def check_in(self):
        if self.check_in_time:
            return datetime.combine(self.date, self.check_in_time)
        return self.created_at

    @property
    def check_out(self):
        if self.check_out_time:
            return datetime.combine(self.date, self.check_out_time)
        return None

    @property
    def method(self):
        return self.notes or self.status.upper()

    def __repr__(self):
        return f"<Attendance Member:{self.member_id} Date:{self.date} Checkin:{self.check_in_time}>"

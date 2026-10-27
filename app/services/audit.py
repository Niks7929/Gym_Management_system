from flask import request
from flask_login import current_user
from app.extensions import db
from app.models.security import AuditLog

def log_audit_event(action, details=None, user=None):
    """
    Log security and administrative actions into the database.
    """
    try:
        actor = user or (current_user if current_user.is_authenticated else None)
        user_id = actor.id if actor else None
        user_email = actor.email if actor else 'Anonymous / System'
        user_role = actor.role if actor else 'Guest'

        ip = request.remote_addr if request else '127.0.0.1'
        ua = request.headers.get('User-Agent', '')[:250] if request else 'System'

        log_entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=action,
            details=details,
            ip_address=ip,
            user_agent=ua
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[Audit Log Error]: {e}")

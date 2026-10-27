from functools import wraps
from datetime import datetime, timedelta
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user
from app.extensions import db
from app.services.audit import log_audit_event

def role_required(allowed_roles):
    """
    Decorator to restrict view access strictly to specific database-verified roles.
    Never trusts client input; checks current_user.role directly.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please authenticate to access your portal dashboard.', 'warning')
                return redirect(url_for('auth.portal', next=request.path))

            if current_user.is_blocked:
                log_audit_event('BLOCKED_USER_ACCESS_ATTEMPT', f'Blocked user attempted access to {request.path}')
                flash('Your account has been locked/suspended by gym administration. Please contact desk.', 'danger')
                return redirect(url_for('auth.logout'))

            if current_user.role not in allowed_roles:
                log_audit_event('UNAUTHORIZED_ACCESS_DENIED', f'Role {current_user.role} attempted to access {request.path} (Allowed: {allowed_roles})')
                flash('Access Denied: You do not possess the required security clearance for this portal.', 'danger')
                
                # Redirect to their own dashboard
                if current_user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif current_user.role == 'receptionist':
                    return redirect(url_for('receptionist.dashboard'))
                elif current_user.role == 'trainer':
                    return redirect(url_for('trainer.dashboard'))
                else:
                    return redirect(url_for('member.dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def handle_failed_login(user, max_attempts=5, lockout_minutes=15):
    """Increment failed login attempts and lock account if exceeded."""
    if not user:
        return
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= max_attempts:
        user.locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
        log_audit_event('ACCOUNT_LOCKED', f'User {user.email} locked for {lockout_minutes} mins after {max_attempts} failed attempts', user)
    else:
        log_audit_event('FAILED_LOGIN', f'Failed login attempt {user.failed_login_attempts}/{max_attempts}', user)
    db.session.commit()

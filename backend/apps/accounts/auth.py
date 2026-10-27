import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.security import HttpBearer
from ninja.errors import HttpError

User = get_user_model()

def create_jwt_token(user) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'full_name': user.full_name,
        'iat': now,
        'exp': now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES)
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HttpError(401, "Token has expired")
    except jwt.InvalidTokenError:
        raise HttpError(401, "Invalid token")

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = decode_jwt_token(token)
            user_id = payload.get('user_id')
            user = User.objects.filter(id=user_id, is_active=True).first()
            if not user:
                return None
            request.auth_user = user
            return user
        except Exception:
            return None

jwt_auth = JWTAuth()

def require_roles(*allowed_roles):
    """
    Helper function to check user role inside endpoint handler.
    Raises 403 Forbidden if user role is not permitted.
    """
    def check_user(user):
        if not user:
            raise HttpError(401, "Authentication required")
        if user.role not in allowed_roles:
            raise HttpError(403, f"Access denied. Required roles: {', '.join(allowed_roles)}")
        return True
    return check_user

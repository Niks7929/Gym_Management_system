from app.routes.public import public_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.trainer import trainer_bp
from app.routes.member import member_bp

__all__ = ['public_bp', 'auth_bp', 'admin_bp', 'trainer_bp', 'member_bp']

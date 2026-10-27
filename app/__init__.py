import os
from flask import Flask, render_template
from config import config_by_name
from app.extensions import db, login_manager, csrf
from app.models.user import User
from app.models.operations import GymSetting

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Context processors for global template variables
    @app.context_processor
    def inject_global_settings():
        try:
            settings = GymSetting.query.first()
        except Exception:
            settings = None
        return dict(gym_settings=settings)

    # Register Blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.trainer import trainer_bp
    from app.routes.member import member_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(trainer_bp, url_prefix='/trainer')
    app.register_blueprint(member_bp, url_prefix='/member')

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app

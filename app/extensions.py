from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.portal'
login_manager.login_message = 'Please authenticate with your portal credentials to access this section.'
login_manager.login_message_category = 'warning'

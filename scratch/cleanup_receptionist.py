from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app('development')
with app.app_context():
    db.session.execute(text("DROP TABLE IF EXISTS receptionists;"))
    db.session.execute(text("DELETE FROM users WHERE role='receptionist' OR email='nikita@gmail.com';"))
    db.session.execute(text("DELETE FROM roles WHERE name='receptionist';"))
    db.session.commit()
    print("Database Cleanup Successful: Receptionist table, user accounts & roles removed from WAMP MySQL.")

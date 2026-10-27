import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from flask import url_for
from app import create_app
from app.extensions import db
from app.models.user import User

class TestAllThreeModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = create_app('testing')
        with app.app_context():
            from app.models.user import Role, MemberProfile, TrainerProfile
            member_role = Role.query.filter_by(name='member').first()
            trainer_role = Role.query.filter_by(name='trainer').first()

            if not User.query.filter_by(email='test_mem@test.com').first():
                u_m = User(email='test_mem@test.com', first_name='Test', last_name='Member', role_id=member_role.id, role='member', is_active=True)
                u_m.set_password('Member@2026!')
                db.session.add(u_m)
                db.session.flush()
                db.session.add(MemberProfile(user_id=u_m.id))

            if not User.query.filter_by(email='test_trn@test.com').first():
                u_t = User(email='test_trn@test.com', first_name='Test', last_name='Trainer', role_id=trainer_role.id, role='trainer', is_active=True)
                u_t.set_password('Trainer@2026!')
                db.session.add(u_t)
                db.session.flush()
                db.session.add(TrainerProfile(user_id=u_t.id))

            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        app = create_app('testing')
        with app.app_context():
            from app.models.user import MemberProfile, TrainerProfile
            for em in ['test_mem@test.com', 'test_trn@test.com']:
                u = User.query.filter_by(email=em).first()
                if u:
                    if u.member_profile:
                        db.session.delete(u.member_profile)
                    if u.trainer_profile:
                        db.session.delete(u.trainer_profile)
                    db.session.delete(u)
            db.session.commit()

    def setUp(self):
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def login_as(self, email, password):
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    # --- 1. ADMIN MODULE TESTS (10 TABS) ---
    def test_01_admin_all_tabs(self):
        print("\n--- Testing Admin Module Tabs ---")
        login_res = self.login_as('admin@setfitgym.com', 'Admin@SetFit2026!')
        self.assertEqual(login_res.status_code, 200)

        admin_endpoints = [
            '/admin/dashboard',
            '/admin/members',
            '/admin/trainers',
            '/admin/plans',
            '/admin/payments',
            '/admin/enquiries',
            '/admin/equipment',
            '/admin/audit-logs',
            '/admin/settings'
        ]

        for ep in admin_endpoints:
            res = self.client.get(ep, follow_redirects=True)
            print(f"  [GET] {ep} -> Status: {res.status_code}")
            self.assertEqual(res.status_code, 200, f"Failed accessing Admin tab {ep}")

    # --- 2. MEMBER MODULE TESTS (5 TABS) ---
    def test_02_member_all_tabs(self):
        print("\n--- Testing Member Module Tabs ---")
        login_res = self.login_as('test_mem@test.com', 'Member@2026!')
        self.assertEqual(login_res.status_code, 200)

        member_endpoints = [
            '/member/dashboard',
            '/member/workout',
            '/member/diet',
            '/member/attendance',
            '/member/payments'
        ]

        for ep in member_endpoints:
            res = self.client.get(ep, follow_redirects=True)
            print(f"  [GET] {ep} -> Status: {res.status_code}")
            self.assertEqual(res.status_code, 200, f"Failed accessing Member tab {ep}")

    # --- 3. TRAINER MODULE TESTS (4 TABS) ---
    def test_03_trainer_all_tabs(self):
        print("\n--- Testing Trainer Module Tabs ---")
        login_res = self.login_as('test_trn@test.com', 'Trainer@2026!')
        self.assertEqual(login_res.status_code, 200)

        trainer_endpoints = [
            '/trainer/dashboard',
            '/trainer/clients',
            '/trainer/workouts_view',
            '/trainer/diets_view'
        ]

        for ep in trainer_endpoints:
            res = self.client.get(ep, follow_redirects=True)
            print(f"  [GET] {ep} -> Status: {res.status_code}")
            self.assertEqual(res.status_code, 200, f"Failed accessing Trainer tab {ep}")

    # --- 4. PUBLIC AND AUTH ROUTES ---
    def test_04_public_and_auth_routes(self):
        print("\n--- Testing Public & Auth Routes ---")
        public_endpoints = [
            '/',
            '/about',
            '/facilities',
            '/trainers',
            '/plans',
            '/contact',
            '/auth/login',
            '/auth/register',
            '/auth/admin-access'
        ]

        for ep in public_endpoints:
            res = self.client.get(ep, follow_redirects=True)
            print(f"  [GET] {ep} -> Status: {res.status_code}")
            self.assertEqual(res.status_code, 200, f"Failed accessing public route {ep}")

    # --- 5. ROLE ISOLATION & ACCESS SECURITY TESTS ---
    def test_05_role_isolation_security(self):
        print("\n--- Testing Role Access Security & Isolation ---")
        # Log in as Member, try to access Admin tab -> Should redirect back to Member Dashboard (302)
        self.login_as('test_mem@test.com', 'Member@2026!')
        res = self.client.get('/admin/dashboard')
        print(f"  [SECURITY] Member accessing Admin Dashboard -> Status: {res.status_code} (Redirected to Member Dashboard)")
        self.assertEqual(res.status_code, 302)

        # Log in as Trainer, try to access Admin tab -> Should redirect back to Trainer Dashboard (302)
        self.login_as('test_trn@test.com', 'Trainer@2026!')
        res = self.client.get('/admin/settings')
        print(f"  [SECURITY] Trainer accessing Admin Settings -> Status: {res.status_code} (Redirected to Trainer Dashboard)")
        self.assertEqual(res.status_code, 302)

if __name__ == '__main__':
    unittest.main()

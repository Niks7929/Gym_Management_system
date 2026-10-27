import sys
import unittest
from flask import url_for
from app import create_app
from app.extensions import db
from app.models.user import User

class TestAllFourModules(unittest.TestCase):
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

    # --- 1. ADMIN MODULE TESTS (11 TABS) ---
    def test_01_admin_all_tabs(self):
        print("\n--- Testing Admin Module Tabs ---")
        login_res = self.login_as('admin@setfitgym.com', 'Admin@SetFit2026!')
        self.assertEqual(login_res.status_code, 200)

        admin_endpoints = [
            '/admin/dashboard',
            '/admin/members',
            '/admin/trainers',
            '/admin/receptionists',
            '/admin/plans',
            '/admin/payments',
            '/admin/attendance',
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
        login_res = self.login_as('gayatri@gmail.com', 'Member@2026!')
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
        login_res = self.login_as('rutuja@gmail.com', 'Trainer@2026!')
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

    # --- 4. RECEPTIONIST MODULE TESTS (6 TABS) ---
    def test_04_receptionist_all_tabs(self):
        print("\n--- Testing Receptionist Module Tabs ---")
        login_res = self.login_as('nikita@gmail.com', 'Desk@2026!')
        self.assertEqual(login_res.status_code, 200)

        receptionist_endpoints = [
            '/receptionist/dashboard',
            '/receptionist/checkin',
            '/receptionist/onboard',
            '/receptionist/renewals',
            '/receptionist/payments',
            '/receptionist/enquiries'
        ]

        for ep in receptionist_endpoints:
            res = self.client.get(ep, follow_redirects=True)
            print(f"  [GET] {ep} -> Status: {res.status_code}")
            self.assertEqual(res.status_code, 200, f"Failed accessing Receptionist tab {ep}")

    # --- 5. PUBLIC AND AUTH ROUTES ---
    def test_05_public_and_auth_routes(self):
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

    # --- 6. ROLE ISOLATION & ACCESS SECURITY TESTS ---
    def test_06_role_isolation_security(self):
        print("\n--- Testing Role Access Security & Isolation ---")
        # Log in as Member, try to access Admin tab -> Should redirect back to Member Dashboard (302)
        self.login_as('gayatri@gmail.com', 'Member@2026!')
        res = self.client.get('/admin/dashboard')
        print(f"  [SECURITY] Member accessing Admin Dashboard -> Status: {res.status_code} (Redirected to Member Dashboard)")
        self.assertEqual(res.status_code, 302)

        # Log in as Trainer, try to access Admin tab -> Should redirect back to Trainer Dashboard (302)
        self.login_as('rutuja@gmail.com', 'Trainer@2026!')
        res = self.client.get('/admin/settings')
        print(f"  [SECURITY] Trainer accessing Admin Settings -> Status: {res.status_code} (Redirected to Trainer Dashboard)")
        self.assertEqual(res.status_code, 302)

if __name__ == '__main__':
    unittest.main()

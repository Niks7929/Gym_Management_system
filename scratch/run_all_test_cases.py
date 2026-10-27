import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import init_db, get_db_connection

class GymSystemFullTestSuite(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-key'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        init_db()

    def test_01_public_landing_page(self):
        """Test public home page rendering"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SETFIT', response.data)
        self.assertIn(b'Transform Your Body', response.data)

    def test_02_public_enquiry_submission(self):
        """Test lead enquiry form from public landing page"""
        response = self.client.post('/home/enquiry', data={
            'full_name': 'Test Lead User',
            'phone': '9876543210',
            'email': 'lead@test.com',
            'plan_id': 1,
            'message': 'Interested in 3-month plan'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'front-desk team will contact you', response.data)

    def test_03_member_registration(self):
        """Test member account registration"""
        import random
        rnd = random.randint(1000, 9999)
        response = self.client.post('/register', data={
            'full_name': f'New Member {rnd}',
            'username': f'newuser_{rnd}',
            'email': f'newuser_{rnd}@gmail.com',
            'phone': f'998877{rnd}',
            'dob': '2000-05-15',
            'gender': 'Male',
            'address': 'Pune, MH',
            'fitness_goal': 'Weight Loss',
            'plan_id': 1,
            'password': 'member123',
            'confirm_password': 'member123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'registration successful', response.data.lower())

    def test_04_admin_login_and_dashboard(self):
        """Test Admin login and dashboard access"""
        login_resp = self.client.post('/login', data={
            'username_or_email': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b'Admin Dashboard', login_resp.data)

        for route in ['/admin/dashboard', '/admin/members', '/admin/plans', '/admin/trainers', '/admin/enquiries', '/admin/attendance', '/admin/reports', '/admin/settings']:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Failed accessing {route}")

    def test_05_receptionist_login_and_dashboard(self):
        """Test Receptionist login and dashboard access"""
        login_resp = self.client.post('/login', data={
            'username_or_email': 'receptionist',
            'password': 'receptionist123'
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b'Receptionist', login_resp.data)

        for route in ['/receptionist/dashboard', '/receptionist/enquiries', '/receptionist/followups', '/receptionist/registrations', '/receptionist/renewals', '/receptionist/attendance']:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Failed accessing {route}")

    def test_06_trainer_login_and_dashboard(self):
        """Test Trainer login and dashboard access"""
        login_resp = self.client.post('/login', data={
            'username_or_email': 'trainer',
            'password': 'trainer123'
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b'Trainer', login_resp.data)

        for route in ['/trainer/dashboard', '/trainer/members', '/trainer/sessions', '/trainer/attendance', '/trainer/workouts', '/trainer/diet', '/trainer/progress', '/trainer/notes']:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Failed accessing {route}")

    def test_07_member_login_and_dashboard(self):
        """Test Member login and dashboard access"""
        login_resp = self.client.post('/login', data={
            'username_or_email': 'member',
            'password': 'member123'
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b'Member Portal', login_resp.data)

        for route in ['/member/dashboard', '/member/profile', '/member/membership', '/member/plan', '/member/trainer', '/member/workouts', '/member/diet', '/member/attendance', '/member/progress', '/member/payments', '/member/offers', '/member/messages']:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Failed accessing {route}")

    def test_08_role_security_protection(self):
        """Test that a Member cannot access Admin or Trainer endpoints"""
        self.client.post('/login', data={'username_or_email': 'member', 'password': 'member123'})

        res = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Access denied', res.data)

        res = self.client.get('/trainer/dashboard', follow_redirects=True)
        self.assertIn(b'Access denied', res.data)

    def test_09_logout(self):
        """Test logout clears session"""
        self.client.post('/login', data={'username_or_email': 'admin', 'password': 'admin123'})
        res = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'logged out', res.data.lower())

if __name__ == '__main__':
    unittest.main()

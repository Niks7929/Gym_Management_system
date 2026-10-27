"""
SETFIT DARK RAGE - Full Comprehensive Verification Test Suite
"""
import unittest
from datetime import date, datetime
from app import create_app
from app.extensions import db
from app.models.user import User, Role, MemberProfile
from app.models.membership import MembershipPlan, Membership, Payment, Enquiry
from app.models.attendance import Attendance

class SetfitDarkRageTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = create_app('testing')
        with app.app_context():
            member_role = Role.query.filter_by(name='member').first()
            trainer_role = Role.query.filter_by(name='trainer').first()

            # Create transient test member
            if not User.query.filter_by(email='temp_test_member@test.com').first():
                m_user = User(
                    email='temp_test_member@test.com',
                    first_name='Test',
                    last_name='Member',
                    phone='+91 99999 11111',
                    role_id=member_role.id,
                    role='member',
                    is_active=True
                )
                m_user.set_password('Member@2026!')
                db.session.add(m_user)
                db.session.flush()
                m_prof = MemberProfile(user_id=m_user.id)
                db.session.add(m_prof)

            # Create transient test trainer
            from app.models.user import TrainerProfile
            if not User.query.filter_by(email='temp_test_trainer@test.com').first():
                t_user = User(
                    email='temp_test_trainer@test.com',
                    first_name='Test',
                    last_name='Trainer',
                    phone='+91 99999 22222',
                    role_id=trainer_role.id,
                    role='trainer',
                    is_active=True
                )
                t_user.set_password('Trainer@2026!')
                db.session.add(t_user)
                db.session.flush()
                t_prof = TrainerProfile(user_id=t_user.id, specialization='Functional Training', experience_years=3)
                db.session.add(t_prof)

            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        app = create_app('testing')
        with app.app_context():
            test_users = User.query.filter(
                (User.email.like('athlete_test_%')) | 
                (User.email.like('athlete_e2e_%')) |
                (User.email == 'temp_test_member@test.com') |
                (User.email == 'temp_test_trainer@test.com')
            ).all()
            for u in test_users:
                if u.member_profile:
                    mem_id = u.member_profile.id
                    Attendance.query.filter_by(member_id=mem_id).delete()
                    Payment.query.filter_by(member_id=mem_id).delete()
                    Membership.query.filter_by(member_id=mem_id).delete()
                    db.session.delete(u.member_profile)
                if u.trainer_profile:
                    db.session.delete(u.trainer_profile)
                db.session.delete(u)
            
            # Clean any test enquiries
            Enquiry.query.filter(
                (Enquiry.email.like('%@test.com')) |
                (Enquiry.email.like('%@example.com'))
            ).delete()

            db.session.commit()

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_homepage_renders_marketing_no_login_form(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SETFIT', response.data)
        self.assertIn(b'GYM', response.data)
        self.assertIn(b'TRANSFORM YOURSELF', response.data)
        # Ensure NO login or registration forms directly on home page
        self.assertNotIn(b'action="/auth/login"', response.data)
        self.assertNotIn(b'action="/auth/register"', response.data)
        self.assertNotIn(b'Join SETFIT GYM Today', response.data)
        print("[PASS] test_01_homepage_renders_marketing_no_login_form")

    def test_02_membership_plans_pricing_exact_six_canonical(self):
        response = self.client.get('/plans')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Monthly Plan', response.data)
        self.assertIn(b'Quarterly Plan', response.data)
        self.assertIn(b'Half-Yearly Plan', response.data)
        self.assertIn(b'Yearly Plan', response.data)
        self.assertIn(b'Premium Annual VIP', response.data)
        self.assertIn(b'Weekend Special', response.data)
        
        # Verify Indian currency pricing values
        self.assertIn(b'1,600', response.data)
        self.assertIn(b'3,500', response.data)
        self.assertIn(b'4,200', response.data)
        self.assertIn(b'7,000', response.data)
        self.assertIn(b'12,000', response.data)
        self.assertIn(b'18,000', response.data)
        
        # Ensure Premium Annual VIP appears exactly ONCE in the rendered page
        vip_count = response.data.count(b'Premium Annual VIP')
        self.assertEqual(vip_count, 1, f"Expected Premium Annual VIP once, got {vip_count}")
        print("[PASS] test_02_membership_plans_pricing_exact_six_canonical")

    def test_03_facilities_and_trainers_pages(self):
        res_fac = self.client.get('/facilities')
        self.assertEqual(res_fac.status_code, 200)
        self.assertIn(b'Iron Facility', res_fac.data)

        res_trn = self.client.get('/trainers')
        self.assertEqual(res_trn.status_code, 200)
        self.assertIn(b'Coaching Roster', res_trn.data)
        print("[PASS] test_03_facilities_and_trainers_pages")

    def test_04_portal_selection_and_role_redirects(self):
        response = self.client.get('/portal', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SETFIT', response.data)
        self.assertIn(b'Sign In', response.data)
        self.assertIn(b'Email Address', response.data)
        self.assertIn(b'Password', response.data)
        self.assertIn(b'Register / Join SETFIT GYM', response.data)
        
        # Test direct login access
        res_login = self.client.get('/auth/login', follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Sign In', res_login.data)
        self.assertIn(b'Register / Join SETFIT GYM', res_login.data)
        print("[PASS] test_04_portal_selection_and_role_redirects")

    def test_05_member_login_flow(self):
        response = self.client.post('/auth/login', data={
            'email': 'temp_test_member@test.com',
            'password': 'Member@2026!',
            'role': 'member'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Member Hub', response.data)
        print("[PASS] test_05_member_login_flow")

    def test_06_trainer_login_flow(self):
        response = self.client.post('/auth/login', data={
            'email': 'temp_test_trainer@test.com',
            'password': 'Trainer@2026!',
            'role': 'trainer'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Trainer', response.data)
        print("[PASS] test_06_trainer_login_flow")

    def test_07_receptionist_login_and_desk_flow(self):
        # 1. Login with dedicated Receptionist account
        response = self.client.post('/auth/login', data={
            'email': 'receptionist@setfitgym.com',
            'password': 'Desk@2026!',
            'role': 'receptionist'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Front Desk', response.data)

        # 2. Check front-desk operations access
        routes = [
            '/receptionist/dashboard',
            '/receptionist/checkin',
            '/receptionist/onboard',
            '/receptionist/renewals',
            '/receptionist/payments',
            '/receptionist/enquiries'
        ]
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} returned {res.status_code}")
        
        # 3. Logout receptionist
        self.client.get('/auth/logout', follow_redirects=True)
        print("[PASS] test_07_receptionist_login_and_desk_flow")

    def test_08_admin_security_passcode_flow(self):
        # Invalid passcode attempt
        res_fail = self.client.post('/auth/admin-access', data={
            'email': 'admin@setfitgym.com',
            'password': 'Admin@SetFit2026!',
            'admin_secret': 'WRONG_SECRET'
        }, follow_redirects=True)
        self.assertIn(b'Invalid Master Admin Passcode', res_fail.data)

        # Valid master passcode attempt
        res_pass = self.client.post('/auth/admin-access', data={
            'email': 'admin@setfitgym.com',
            'password': 'Admin@SetFit2026!',
            'admin_secret': 'SETFIT_MASTER_ADMIN_PASSCODE_2026'
        }, follow_redirects=True)
        self.assertEqual(res_pass.status_code, 200)
        self.assertIn(b'Executive Analytics', res_pass.data)
        print("[PASS] test_08_admin_security_passcode_flow")

    def test_09_enquiry_lead_submission(self):
        response = self.client.post('/enquiry/submit', data={
            'full_name': 'Prospect Lead',
            'phone': '+91 99887 76655',
            'email': 'lead@test.com',
            'interested_program': 'Powerlifting & Heavy Strength',
            'message': 'Interested in joining for competition prep.'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        enquiry = Enquiry.query.filter_by(email='lead@test.com').first()
        self.assertIsNotNone(enquiry)
        self.assertEqual(enquiry.name, 'Prospect Lead')
        print("[PASS] test_09_enquiry_lead_submission")

    def test_10_member_registration_strictly_member_role(self):
        # Public registration creates member role ONLY
        plan = MembershipPlan.query.first()
        email = f"athlete_test_{int(datetime.utcnow().timestamp())}@test.com"
        response = self.client.post('/auth/register', data={
            'full_name': 'Test Athlete',
            'email': email,
            'phone': '+91 98765 77777',
            'emergency_contact': '+91 98765 88888',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'plan_id': plan.id,
            'medical_conditions': 'No injuries'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        created_user = User.query.filter_by(email=email).first()
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.role, 'member')
        self.assertIsNotNone(created_user.member_profile)
        print("[PASS] test_10_member_registration_strictly_member_role")

    def test_11_logout_clears_session(self):
        self.client.post('/auth/login', data={
            'email': 'temp_test_member@test.com',
            'password': 'Member@2026!',
            'role': 'member'
        }, follow_redirects=True)

        res_logout = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertIn(b'TRANSFORM YOURSELF', res_logout.data)
        print("[PASS] test_11_logout_clears_session")

    def test_12_end_to_end_payment_and_admin_verification(self):
        plan = MembershipPlan.query.first()
        test_email = f"athlete_e2e_{int(datetime.utcnow().timestamp())}@domain.com"
        
        # 1. Register new athlete member
        reg_res = self.client.post('/auth/register', data={
            'full_name': 'E2E Athlete',
            'email': test_email,
            'phone': '+91 99999 77777',
            'emergency_contact': '+91 99999 88888',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'plan_id': plan.id
        }, follow_redirects=True)
        self.assertEqual(reg_res.status_code, 200)
        
        user = User.query.filter_by(email=test_email).first()
        self.assertIsNotNone(user)
        mem = user.member_profile.memberships[0]
        self.assertEqual(mem.status, 'pending_verification')

        # 2. Member submits 12-digit UTR
        utr_res = self.client.post('/member/submit-utr', data={'utr_number': '987654321098'}, follow_redirects=True)
        self.assertEqual(utr_res.status_code, 200)
        
        pay = Payment.query.filter_by(member_id=user.member_profile.id).first()
        self.assertEqual(pay.utr_number, '987654321098')
        self.assertEqual(pay.status, 'pending_verification')

        # Logout member
        self.client.get('/auth/logout', follow_redirects=True)

        # 3. Master Admin logs in
        admin_login = self.client.post('/auth/admin-access', data={
            'email': 'admin@setfitgym.com',
            'password': 'Admin@SetFit2026!',
            'admin_secret': 'SETFIT_MASTER_ADMIN_PASSCODE_2026'
        }, follow_redirects=True)
        self.assertEqual(admin_login.status_code, 200)

        # 4. Master Admin verifies payment
        verify_res = self.client.post(f'/admin/payments/verify/{pay.id}', follow_redirects=True)
        self.assertEqual(verify_res.status_code, 200)

        db.session.refresh(mem)
        db.session.refresh(pay)
        self.assertEqual(pay.status, 'completed')
        self.assertEqual(mem.status, 'active')
        self.assertTrue(mem.is_verified)
        print("[PASS] test_12_end_to_end_payment_and_admin_verification")

    def test_13_single_admin_single_receptionist_and_encryption_integrity(self):
        # 1. Verify Exactly 1 Master Admin in system
        admins = User.query.filter_by(role='admin').all()
        self.assertEqual(len(admins), 1, f"Expected exactly 1 admin, found {len(admins)}")
        admin = admins[0]
        self.assertEqual(admin.email, 'admin@setfitgym.com')

        # 2. Verify Exactly 1 Front Desk Receptionist in system
        receptionists = User.query.filter_by(role='receptionist').all()
        self.assertEqual(len(receptionists), 1, f"Expected exactly 1 receptionist, found {len(receptionists)}")
        rec = receptionists[0]
        self.assertEqual(rec.email, 'receptionist@setfitgym.com')

        # 3. Verify Admin Password Encryption (Cryptographic Hash)
        self.assertIsNotNone(admin.password_hash)
        self.assertNotEqual(admin.password_hash, 'Admin@SetFit2026!')
        self.assertTrue(admin.password_hash.startswith(('scrypt:', 'pbkdf2:')))
        self.assertTrue(admin.check_password('Admin@SetFit2026!'))
        self.assertFalse(admin.check_password('IncorrectPassword'))

        # 4. Verify Receptionist Password Encryption
        self.assertIsNotNone(rec.password_hash)
        self.assertNotEqual(rec.password_hash, 'Desk@2026!')
        self.assertTrue(rec.password_hash.startswith(('scrypt:', 'pbkdf2:')))
        self.assertTrue(rec.check_password('Desk@2026!'))
        self.assertFalse(rec.check_password('WrongPass'))

        # 5. Verify Registration Page includes Front Desk / Receptionist option
        reg_page_res = self.client.get('/auth/register')
        self.assertEqual(reg_page_res.status_code, 200)
        self.assertIn(b'Front Desk / Receptionist', reg_page_res.data)

        # 6. Verify attempting to register duplicate receptionist is blocked
        dup_rec_res = self.client.post('/auth/register', data={
            'role': 'receptionist',
            'full_name': 'Duplicate Receptionist',
            'email': 'another_rec@test.com',
            'phone': '+91 99999 00000',
            'password': 'Password123!'
        }, follow_redirects=True)
        self.assertIn(b'Only 1 official Front Desk / Receptionist account is allowed', dup_rec_res.data)
        # Ensure still only 1 receptionist exists
        self.assertEqual(User.query.filter_by(role='receptionist').count(), 1)

        # 7. Verify Receptionist is strictly blocked from Admin terminal
        self.client.post('/auth/login', data={
            'email': 'receptionist@setfitgym.com',
            'password': 'Desk@2026!',
            'role': 'receptionist'
        }, follow_redirects=True)
        admin_res = self.client.get('/admin/dashboard', follow_redirects=True)
        # Should be redirected / unauthorized
        self.assertNotIn(b'Executive Analytics', admin_res.data)
        self.client.get('/auth/logout', follow_redirects=True)

        print("[PASS] test_13_single_admin_single_receptionist_and_encryption_integrity")

    def test_14_landing_inquiry_to_receptionist_and_trainer_assignment_flow(self):
        # 1. Visitor submits enquiry from landing page
        enq_res = self.client.post('/enquiry/submit', data={
            'full_name': 'Rohan Joshi',
            'phone': '+91 98220 12345',
            'email': 'rohan.joshi@test.com',
            'interested_program': 'Powerlifting & Hypertrophy',
            'message': 'Interested in joining SETFIT gym.'
        }, follow_redirects=True)
        self.assertEqual(enq_res.status_code, 200)

        # 2. Receptionist logs in and checks Lead Desk
        self.client.post('/auth/login', data={
            'email': 'receptionist@setfitgym.com',
            'password': 'Desk@2026!',
            'role': 'receptionist'
        }, follow_redirects=True)
        rec_lead_res = self.client.get('/receptionist/enquiries')
        self.assertEqual(rec_lead_res.status_code, 200)
        self.assertIn(b'Rohan Joshi', rec_lead_res.data)
        self.client.get('/auth/logout', follow_redirects=True)

        # 3. Master Admin assigns coach to member
        member_user = User.query.filter_by(email='temp_test_member@test.com').first()
        trainer_user = User.query.filter_by(email='temp_test_trainer@test.com').first()
        self.assertIsNotNone(member_user)
        self.assertIsNotNone(trainer_user)

        self.client.post('/auth/admin-access', data={
            'email': 'admin@setfitgym.com',
            'password': 'Admin@SetFit2026!',
            'admin_secret': 'SETFIT_MASTER_ADMIN_PASSCODE_2026'
        }, follow_redirects=True)

        assign_res = self.client.post('/admin/members/assign-coach', data={
            'member_id': member_user.member_profile.id,
            'trainer_id': trainer_user.trainer_profile.id
        }, follow_redirects=True)
        self.assertEqual(assign_res.status_code, 200)
        self.client.get('/auth/logout', follow_redirects=True)

        # 4. Trainer logs in and sees assigned member in roster
        self.client.post('/auth/login', data={
            'email': 'temp_test_trainer@test.com',
            'password': 'Trainer@2026!',
            'role': 'trainer'
        }, follow_redirects=True)
        trainer_dash = self.client.get('/trainer/dashboard')
        self.assertEqual(trainer_dash.status_code, 200)
        self.assertIn(b'Test Member', trainer_dash.data)

        # Trainer creates custom workout split for this member
        wo_res = self.client.post('/trainer/workouts/create', data={
            'member_id': member_user.member_profile.id,
            'title': 'Bulking Heavy Split',
            'goal': 'Strength & Hypertrophy',
            'days_per_week': 5,
            'description': 'Heavy compound lifting progression'
        }, follow_redirects=True)
        self.assertEqual(wo_res.status_code, 200)
        self.client.get('/auth/logout', follow_redirects=True)

        # 5. Member logs in and sees assigned coach & workout split
        self.client.post('/auth/login', data={
            'email': 'temp_test_member@test.com',
            'password': 'Member@2026!',
            'role': 'member'
        }, follow_redirects=True)
        member_dash = self.client.get('/member/dashboard')
        self.assertEqual(member_dash.status_code, 200)
        self.assertIn(b'Test Trainer', member_dash.data)
        self.assertIn(b'Bulking Heavy Split', member_dash.data)

        # Member views full workout details
        member_wo = self.client.get('/member/workout')
        self.assertEqual(member_wo.status_code, 200)
        self.assertIn(b'Bulking Heavy Split', member_wo.data)
        self.client.get('/auth/logout', follow_redirects=True)

        print("[PASS] test_14_landing_inquiry_to_receptionist_and_trainer_assignment_flow")

    def test_15_role_specific_registration_fields_and_plans_isolation(self):
        # 1. Register Trainer with trainer-specific fields (No Plan)
        t_email = f"coach_auto_{int(datetime.utcnow().timestamp())}@test.com"
        reg_t = self.client.post('/auth/register', data={
            'role': 'trainer',
            'full_name': 'Automated Coach',
            'email': t_email,
            'phone': '+91 98888 11111',
            'password': 'Password123!',
            'specialization': 'Powerlifting & Heavy Lifts',
            'experience_years': 4,
            'certifications': 'ISSA Certified'
        }, follow_redirects=True)
        self.assertEqual(reg_t.status_code, 200)

        created_trainer = User.query.filter_by(email=t_email).first()
        self.assertIsNotNone(created_trainer)
        self.assertEqual(created_trainer.role, 'trainer')
        self.assertIsNotNone(created_trainer.trainer_profile)
        self.assertEqual(created_trainer.trainer_profile.specialization, 'Powerlifting & Heavy Lifts')
        self.assertEqual(created_trainer.trainer_profile.experience_years, 4)
        self.assertIsNone(created_trainer.member_profile)

        # Cleanup
        db.session.delete(created_trainer.trainer_profile)
        db.session.delete(created_trainer)
        db.session.commit()
        print("[PASS] test_15_role_specific_registration_fields_and_plans_isolation")

if __name__ == '__main__':
    unittest.main()

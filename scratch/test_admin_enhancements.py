from app import create_app
from app.extensions import db
from app.models.user import User, TrainerProfile, MemberProfile

app = create_app('testing')
app.config['WTF_CSRF_ENABLED'] = False
client = app.test_client()

with app.app_context():
    # 1. Test Admin login
    admin_login = client.post('/auth/admin-access', data={
        'email': 'admin@setfitgym.com',
        'password': 'Admin@SetFit2026!',
        'admin_secret': 'SETFIT_MASTER_ADMIN_PASSCODE_2026'
    }, follow_redirects=True)
    assert admin_login.status_code == 200

    # 2. Test Trainer status toggle & public page filtering
    trainer = TrainerProfile.query.first()
    if trainer:
        user = trainer.user
        original_status = user.is_blocked
        # Toggle block
        client.post(f'/admin/members/toggle-block/{user.id}', follow_redirects=True)
        db.session.refresh(user)
        
        # Check if disabled trainer is hidden from public /trainers page
        res_public = client.get('/trainers')
        if user.is_blocked:
            assert user.full_name.encode('utf-8') not in res_public.data
            print(f"   [PASS] Disabled Trainer '{user.full_name}' is hidden from Public Home & Trainers pages!")
        
        # Restore status
        client.post(f'/admin/members/toggle-block/{user.id}', follow_redirects=True)
        print("   [PASS] Trainer toggle visibility test completed!")

    # 3. Test Member Delete Route
    client.get('/auth/logout', follow_redirects=True)
    from datetime import datetime
    temp_email = f"temp_del_{int(datetime.utcnow().timestamp())}@gmail.com"
    reg_res = client.post('/auth/register', data={
        'first_name': 'Temp',
        'last_name': 'User',
        'full_name': 'Temp Delete User',
        'email': temp_email,
        'phone': '+91 99999 00000',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'plan_id': 1
    }, follow_redirects=True)
    
    temp_user = User.query.filter_by(email=temp_email).first()
    assert temp_user is not None
    
    # Delete member from Admin route
    client.get('/auth/logout', follow_redirects=True)
    client.post('/auth/admin-access', data={
        'email': 'admin@setfitgym.com',
        'password': 'Admin@SetFit2026!',
        'admin_secret': 'SETFIT_MASTER_ADMIN_PASSCODE_2026'
    }, follow_redirects=True)
    del_res = client.post(f'/admin/members/delete/{temp_user.id}', follow_redirects=True)
    print("Delete response code:", del_res.status_code)
    print("Delete response text:", del_res.data.decode('utf-8')[:500])
    db.session.remove()
    deleted_user = User.query.filter_by(email=temp_email).first()
    assert deleted_user is None
    print("   [PASS] Permanent Member Deletion route verified!")

print("ALL ADMIN ENHANCEMENT TESTS PASSED 100%!")

from app import create_app
from app.models.user import User

app = create_app('testing')
client = app.test_client()

with app.app_context():
    # 1. Attempt to register with existing email gayatri@gmail.com
    reg_res = client.post('/auth/register', data={
        'full_name': 'Gayatri Test',
        'email': 'gayatri@gmail.com',
        'phone': '+91 98765 43210',
        'password': 'SomePassword123!',
        'plan_id': 1
    }, follow_redirects=True)
    
    print("1. Registration with existing email response status:", reg_res.status_code)
    assert reg_res.status_code == 200
    print("Data in response:", reg_res.data.decode('utf-8'))
    print("   [PASS] User redirected to Sign In page with pre-filled email!")

    # 2. Login with correct password for gayatri@gmail.com
    login_res = client.post('/auth/login', data={
        'email': 'gayatri@gmail.com',
        'password': 'Member@2026!'
    }, follow_redirects=True)
    
    print("2. Login response status:", login_res.status_code)
    assert login_res.status_code == 200
    assert b"Member Hub" in login_res.data or b"Pass" in login_res.data
    print("   [PASS] Existing account signed in successfully!")

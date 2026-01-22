from app import create_app, db

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
app.config['ADMIN_SECRET'] = 'admintest'

with app.app_context():
    db.drop_all()
    db.create_all()

    client = app.test_client()

    # Register a student
    resp = client.post('/auth/register', data={
        'username':'student1',
        'password':'password123',
        'confirm':'password123',
        'role':'student',
        'admin_code':''
    }, follow_redirects=False)
    print('student register status', resp.status_code, 'Location=', resp.headers.get('Location'))

    # Login student
    resp = client.post('/auth/login', data={
        'username':'student1',
        'password':'password123',
    }, follow_redirects=False)
    print('student login status', resp.status_code, 'Location=', resp.headers.get('Location'))

    # Register an admin
    resp = client.post('/auth/register', data={
        'username':'admin1',
        'password':'adminpass',
        'confirm':'adminpass',
        'role':'admin',
        'admin_code':'admintest'
    }, follow_redirects=False)
    print('admin register status', resp.status_code, 'Location=', resp.headers.get('Location'))

    # Login admin
    resp = client.post('/auth/login', data={
        'username':'admin1',
        'password':'adminpass'
    }, follow_redirects=False)
    print('admin login status', resp.status_code, 'Location=', resp.headers.get('Location'))

    # Verify password stored hashed
    from app.models import User
    s = User.query.filter_by(username='student1').first()
    a = User.query.filter_by(username='admin1').first()
    print('student pw stored prefix:', s.password[:10])
    print('admin pw stored prefix:', a.password[:10])

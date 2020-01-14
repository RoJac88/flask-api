from app.models import User

tokens = { 'admin': None, 'user': None}

def test_login(client, db):
    """Tests for the login endpoint"""

    # Empty request:
    res = client.post('/login')
    assert res.status_code == 400
    json = res.get_json()
    assert json.get('name') == 'Bad Request'
    assert json.get('code') == 400
    assert json.get('description') == 'Missing JSON in request'

    # Missing password:
    res = client.post('/login', json={
        'username': 'admin'
    })
    assert res.status_code == 400
    json = res.get_json()
    assert json.get('name') == 'Bad Request'
    assert json.get('code') == 400
    assert json.get('description') == 'Missing password parameter'

    # Invalid Credentials:
    res = client.post('/login', json={
        'username': 'idontexist',
        'password': 'password'
    })
    assert res.status_code == 401
    json = res.get_json()
    assert json.get('name') == 'Unauthorized'
    assert json.get('code') == 401
    assert json.get('description') == 'Bad username or passowrd'

    # Login Admin
    res = client.post('/login', json={
        'username': 'admin',
        'password': 'admin'
    })
    assert res.status_code == 200
    json = res.get_json()
    assert 'access_token' in json
    admin_token = json.get('access_token', None)
    assert admin_token is not None
    tokens['admin'] = admin_token

    # Login User
    res = client.post('/login', json={
        'username': 'user',
        'password': 'user'
    })
    assert res.status_code == 200
    json = res.get_json()
    assert 'access_token' in json
    user_token = json.get('access_token', None)
    assert user_token is not None
    tokens['user'] = user_token

def test_register(client, db):
    """Tests for user registration endpoint"""

    # Empty request:
    res = client.post('/register')
    assert res.status_code == 401
    json = res.get_json()
    assert json.get('name') == 'Unauthorized'
    assert json.get('code') == 401
    assert json.get('description') == 'Missing Authorization Header'

    # Register new user with admin toekn:
    admin_token = tokens['admin']
    assert admin_token is not None
    res = client.post('/register', 
    headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={
        'username': 'new_user',
        'email': 'newuser@email.com',
        'password': 'new'
    })
    json = res.get_json()
    assert res.status_code == 201
    assert json.get('email') == 'newuser@email.com'
    assert json.get('username') == 'new_user'
    assert json.get('role') == 1
    assert json.get('password', None) is None
    assert json.get('password_hash', None) is None
    created_user = User.query.filter_by(username='new_user').first()
    assert created_user is not None
    assert created_user.role == 1
    assert created_user.email == 'newuser@email.com'
    _id = json.get('id')
    assert created_user.id == _id
    assert created_user.password_hash is not None
    assert created_user.check_password('new')

    # Register new user with non admin token:
    user_token = tokens['user']
    assert user_token is not None
    res = client.post('/register', 
    headers={
        'Authorization': f'Bearer {user_token}'
    }, json={
        'username': 'new_user2',
        'email': 'newuser2@email.com',
        'password': 'new2'
    })
    assert res.status_code == 403
    json = res.get_json()
    assert json.get('name') == 'Forbidden'
    assert json.get('code') == 403
    assert json.get('description') == 'You are not allowed to view this resource'
    assert User.query.filter_by(username='new_user2').first() is None

    # Existing username
    res = client.post('/register', 
    headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={
        'username': 'admin',
        'email': 'newuser2@email.com',
        'password': 'admin'
    })
    json = res.get_json()
    assert res.status_code == 409
    assert json.get('name') == 'Conflict'
    assert json.get('code') == 409
    assert json.get('description') == 'Username already registered'
    assert len(list(User.query.filter_by(username='admin'))) == 1

    # Existing email
    res = client.post('/register', 
    headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={
        'username': 'Jack Sparrow',
        'email': 'admin@email.com',
        'password': 'blackpearl'
    })
    json = res.get_json()
    assert res.status_code == 409
    assert json.get('name') == 'Conflict'
    assert json.get('code') == 409
    assert json.get('description') == 'Email already registered'
    assert len(list(User.query.filter_by(email='admin@email.com'))) == 1

def test_users(client, db):
    """Tests for all users endpoint"""

    # Empty request:
    res = client.get('/users')
    assert res.status_code == 401
    json = res.get_json()
    assert json.get('name') == 'Unauthorized'
    assert json.get('code') == 401
    assert json.get('description') == 'Missing Authorization Header'

    # Access with non admin token:
    user_token = tokens['user']
    assert user_token is not None
    res = client.get('/users', 
        headers={'Authorization': f'Bearer {user_token}'})
    assert res.status_code == 403
    json = res.get_json()
    assert json.get('name') == 'Forbidden'
    assert json.get('code') == 403
    assert json.get('description') == 'You are not allowed to view this resource'

    # Access with admin token
    admin_token = tokens['admin']
    assert admin_token is not None
    res = client.get('/users', 
        headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    json = res.get_json()
    assert len(json) > 1
    assert json[0].get('id') == 1
    assert json[0].get('username') == 'admin'
    assert json[0].get('email') == "admin@email.com"
    assert json[0].get('role') == 0
    assert "created_at" in json[0]
    assert json[1].get('id') == 2
    assert json[1].get('username') == 'user'
    assert json[1].get('email') == "user@email.com"
    assert json[1].get('role') == 1
    assert "created_at" in json[1]
    assert "password_hash" not in json[0]

def test_get_user(client, db):
    """Tests for single user information endpoint"""
    admin_token = tokens['admin']
    user_token = tokens['user']

    # Missing Authorization Header:
    res = client.get('/users/1')
    assert res.status_code == 401
    json = res.get_json()
    assert json.get('name') == 'Unauthorized'
    assert json.get('code') == 401
    assert json.get('description') == 'Missing Authorization Header'

    # Access with non admin token:
    assert user_token is not None
    res = client.get('/users/1', 
        headers={'Authorization': f'Bearer {user_token}'})
    assert res.status_code == 403
    json = res.get_json()
    assert json.get('name') == 'Forbidden'
    assert json.get('code') == 403
    assert json.get('description') == 'You are not allowed to view this resource'

    # Access with admin token
    assert admin_token is not None
    res = client.get('/users/1', 
        headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    json = res.get_json()
    assert "created_at" in json
    assert json.get('id') == 1
    assert json.get('role') == 0
    assert json.get('username') == 'admin'
    assert json.get('email') == 'admin@email.com'
    assert "password_hash" not in json

    # Access non existing user id
    res = client.get('/users/666', 
        headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 404
    json = res.get_json()
    assert json.get('name') == 'Not Found'
    assert json.get('code') == 404
    assert json.get('description') == 'User not found'

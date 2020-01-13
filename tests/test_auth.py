from app.models import User

tokens = { 'admin': None, 'user': None}

def test_login(client):
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

def test_register(client):
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

def test_users(client):
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
    assert "password_hash" not in json[0]

def test_get_user(client):
    """Tests for single user information endpoint"""
    pass 
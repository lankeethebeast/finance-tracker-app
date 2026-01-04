import pytest
from app import app, db
from models.user import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123'
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User registered successfully'
    assert data['user']['username'] == 'testuser'

def test_register_duplicate_username(client):
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test1@example.com',
        'password': 'TestPassword123'
    })

    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'TestPassword456'
    })

    assert response.status_code == 400
    data = response.get_json()
    assert 'already exists' in data['error']

def test_login(client):
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123'
    })

    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'TestPassword123'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['message'] == 'Login successful'

def test_login_invalid_credentials(client):
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })

    assert response.status_code == 401
    data = response.get_json()
    assert 'Invalid' in data['error']

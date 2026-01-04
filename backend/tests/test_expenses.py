import pytest
from app import app, db
from models.user import User
from models.expense import Expense
import json


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test user with proper bcrypt hash
            from extensions import bcrypt
            password_hash = bcrypt.generate_password_hash('testpassword123').decode('utf-8')
            test_user = User(username='testuser', email='test@example.com', password_hash=password_hash, role='user')
            db.session.add(test_user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def auth_token(client):
    # Login to get token
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpassword123'
    })
    return response.get_json()['access_token']


def test_create_expense(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.post('/api/expenses/', json={
        'amount': 50.0,
        'category': 'Food',
        'description': 'Lunch',
        'transaction_type': 'expense',
        'date': '2025-01-01'
    }, headers=headers)

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Expense created successfully'
    assert data['expense']['amount'] == 50.0
    assert data['expense']['category'] == 'Food'


def test_get_expenses(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Create test expenses
    client.post('/api/expenses/', json={
        'amount': 25.0, 'category': 'Food', 'transaction_type': 'expense', 'date': '2025-01-01'
    }, headers=headers)
    client.post('/api/expenses/', json={
        'amount': 75.0, 'category': 'Transport', 'transaction_type': 'expense', 'date': '2025-01-02'
    }, headers=headers)

    response = client.get('/api/expenses/', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['expenses']) == 2


def test_update_expense(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Create expense
    create_response = client.post('/api/expenses/', json={
        'amount': 50.0, 'category': 'Food', 'transaction_type': 'expense', 'date': '2025-01-01'
    }, headers=headers)
    expense_id = create_response.get_json()['expense']['id']

    # Update expense
    response = client.put(f'/api/expenses/{expense_id}', json={
        'amount': 60.0, 'category': 'Food', 'description': 'Updated lunch'
    }, headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['expense']['amount'] == 60.0
    assert data['expense']['description'] == 'Updated lunch'


def test_delete_expense(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Create expense
    create_response = client.post('/api/expenses/', json={
        'amount': 50.0, 'category': 'Food', 'transaction_type': 'expense', 'date': '2025-01-01'
    }, headers=headers)
    expense_id = create_response.get_json()['expense']['id']

    # Delete expense
    response = client.delete(f'/api/expenses/{expense_id}', headers=headers)
    assert response.status_code == 200

    # Verify deletion
    get_response = client.get('/api/expenses/', headers=headers)
    assert len(get_response.get_json()['expenses']) == 0


def test_get_expense_summary(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Create test data
    client.post('/api/expenses/', json={
        'amount': 100.0, 'category': 'Income', 'transaction_type': 'income', 'date': '2025-01-01'
    }, headers=headers)
    client.post('/api/expenses/', json={
        'amount': 50.0, 'category': 'Food', 'transaction_type': 'expense', 'date': '2025-01-01'
    }, headers=headers)
    client.post('/api/expenses/', json={
        'amount': 25.0, 'category': 'Transport', 'transaction_type': 'expense', 'date': '2025-01-02'
    }, headers=headers)

    response = client.get('/api/expenses/summary', headers=headers)
    assert response.status_code == 200
    data = response.get_json()

    assert data['total_income'] == 100.0
    assert data['total_expenses'] == 75.0
    assert data['balance'] == 25.0
    assert len(data['category_breakdown']) == 2


def test_expense_validation(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Test missing required fields
    response = client.post('/api/expenses/', json={
        'amount': 50.0
        # Missing category and transaction_type
    }, headers=headers)
    assert response.status_code == 400

    # Test invalid transaction type
    response = client.post('/api/expenses/', json={
        'amount': 50.0, 'category': 'Food', 'transaction_type': 'invalid'
    }, headers=headers)
    assert response.status_code == 400


def test_expense_filtering(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Create test expenses
    client.post('/api/expenses/', json={
        'amount': 50.0, 'category': 'Food', 'transaction_type': 'expense', 'date': '2025-01-01'
    }, headers=headers)
    client.post('/api/expenses/', json={
        'amount': 100.0, 'category': 'Income', 'transaction_type': 'income', 'date': '2025-01-02'
    }, headers=headers)
    client.post('/api/expenses/', json={
        'amount': 25.0, 'category': 'Transport', 'transaction_type': 'expense', 'date': '2025-01-03'
    }, headers=headers)

    # Filter by category
    response = client.get('/api/expenses/?category=Food', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['expenses']) == 1
    assert data['expenses'][0]['category'] == 'Food'

    # Filter by transaction type
    response = client.get('/api/expenses/?type=income', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['expenses']) == 1
    assert data['expenses'][0]['transaction_type'] == 'income'

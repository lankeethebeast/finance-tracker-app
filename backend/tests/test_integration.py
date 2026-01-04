import pytest
from app import app, db
from models.user import User
from models.expense import Expense
from datetime import datetime, timedelta


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


def test_full_user_workflow(client):
    """Test complete user registration, login, and data management workflow"""

    # 1. Register a new user
    register_response = client.post('/api/auth/register', json={
        'username': 'integration_user',
        'email': 'integration@example.com',
        'password': 'TestPassword123'
    })
    assert register_response.status_code == 201
    register_data = register_response.get_json()
    assert register_data['message'] == 'User registered successfully'
    assert register_data['user']['username'] == 'integration_user'
    assert register_data['user']['role'] == 'user'

    # 2. Login with the new user
    login_response = client.post('/api/auth/login', json={
        'username': 'integration_user',
        'password': 'TestPassword123'
    })
    assert login_response.status_code == 200
    login_data = login_response.get_json()
    assert 'access_token' in login_data
    assert login_data['message'] == 'Login successful'
    assert login_data['user']['username'] == 'integration_user'

    token = login_data['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 3. Get current user info
    me_response = client.get('/api/auth/me', headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.get_json()
    assert me_data['user']['username'] == 'integration_user'
    assert me_data['user']['role'] == 'user'

    # 4. Create some expenses
    expenses_data = [
        {'amount': 50.0, 'category': 'Food', 'transaction_type': 'expense', 'date': '2025-01-01'},
        {'amount': 100.0, 'category': 'Income', 'transaction_type': 'income', 'date': '2025-01-01'},
        {'amount': 25.0, 'category': 'Transport', 'transaction_type': 'expense', 'date': '2025-01-02'},
        {'amount': 75.0, 'category': 'Food', 'transaction_type': 'expense', 'date': '2025-01-02'},
    ]

    created_expenses = []
    for expense_data in expenses_data:
        response = client.post('/api/expenses/', json=expense_data, headers=headers)
        assert response.status_code == 201
        created_expenses.append(response.get_json()['expense'])

    # 5. Get all expenses
    expenses_response = client.get('/api/expenses/', headers=headers)
    assert expenses_response.status_code == 200
    expenses_data = expenses_response.get_json()
    assert len(expenses_data['expenses']) == 4

    # 6. Get expense summary
    summary_response = client.get('/api/expenses/summary', headers=headers)
    assert summary_response.status_code == 200
    summary_data = summary_response.get_json()
    assert summary_data['total_income'] == 100.0
    assert summary_data['total_expenses'] == 150.0  # 50 + 25 + 75
    assert summary_data['balance'] == -50.0

    # 7. Update an expense
    expense_id = created_expenses[0]['id']
    update_response = client.put(f'/api/expenses/{expense_id}', json={
        'amount': 60.0, 'category': 'Food', 'description': 'Updated lunch'
    }, headers=headers)
    assert update_response.status_code == 200

    # Verify update
    get_response = client.get(f'/api/expenses/{expense_id}', headers=headers)
    assert get_response.status_code == 200
    updated_expense = get_response.get_json()['expense']
    assert updated_expense['amount'] == 60.0
    assert updated_expense['description'] == 'Updated lunch'

    # 8. Test filtering
    food_expenses = client.get('/api/expenses/?category=Food', headers=headers)
    assert food_expenses.status_code == 200
    food_data = food_expenses.get_json()
    assert len(food_data['expenses']) == 2  # Two food expenses

    income_expenses = client.get('/api/expenses/?type=income', headers=headers)
    assert income_expenses.status_code == 200
    income_data = income_expenses.get_json()
    assert len(income_data['expenses']) == 1  # One income entry

    # 9. Delete an expense
    delete_response = client.delete(f'/api/expenses/{expense_id}', headers=headers)
    assert delete_response.status_code == 200

    # Verify deletion
    final_expenses = client.get('/api/expenses/', headers=headers)
    assert len(final_expenses.get_json()['expenses']) == 3


def test_admin_workflow(client):
    """Test admin user workflow including user management"""

    # 1. Register admin user
    admin_register = client.post('/api/auth/register', json={
        'username': 'admin_user',
        'email': 'admin@example.com',
        'password': 'AdminPass123',
        'role': 'admin'
    })
    assert admin_register.status_code == 201

    # 2. Login as admin
    admin_login = client.post('/api/auth/login', json={
        'username': 'admin_user',
        'password': 'AdminPass123'
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.get_json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}

    # 3. Register a regular user as admin
    user_register = client.post('/api/auth/register', json={
        'username': 'regular_user',
        'email': 'regular@example.com',
        'password': 'UserPass123',
        'role': 'user'
    }, headers=admin_headers)
    assert user_register.status_code == 201

    # 4. Get all users (admin only)
    users_response = client.get('/api/auth/users', headers=admin_headers)
    assert users_response.status_code == 200
    users_data = users_response.get_json()
    assert len(users_data['users']) == 2  # admin + regular user

    # Verify roles
    user_roles = [user['role'] for user in users_data['users']]
    assert 'admin' in user_roles
    assert 'user' in user_roles

    # 5. Try to access admin endpoint as regular user (should fail)
    regular_login = client.post('/api/auth/login', json={
        'username': 'regular_user',
        'password': 'UserPass123'
    })
    assert regular_login.status_code == 200
    regular_token = regular_login.get_json()['access_token']
    regular_headers = {'Authorization': f'Bearer {regular_token}'}

    # This should fail with 403
    admin_only_response = client.get('/api/auth/users', headers=regular_headers)
    assert admin_only_response.status_code == 403
    error_data = admin_only_response.get_json()
    assert 'Insufficient permissions' in error_data['error']


def test_analytics_workflow(client):
    """Test complete analytics workflow"""

    # 1. Register and login user
    client.post('/api/auth/register', json={
        'username': 'analytics_user',
        'email': 'analytics@example.com',
        'password': 'AnalyticsPass123'
    })

    login_response = client.post('/api/auth/login', json={
        'username': 'analytics_user',
        'password': 'AnalyticsPass123'
    })
    token = login_response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Create sufficient expense data for analytics (15+ entries) across multiple months
    for month in [1, 2, 3]:  # January, February, March
        for i in range(7):  # 7 expenses per month
            expense_data = {
                'amount': 40.0 + (month-1) * 20 + i * 2,  # Increasing amounts
                'category': 'Food' if i % 2 == 0 else 'Transport',
                'transaction_type': 'expense' if i < 5 else 'income',  # Mix of income and expenses
                'date': f'2025-{month:02d}-{i+1:02d}',
                'description': f'Expense {month}-{i+1}'
            }
            client.post('/api/expenses/', json=expense_data, headers=headers)

    # 3. Test predictions (should work with 20 data points)
    predict_response = client.get('/api/analytics/predict?days=7', headers=headers)
    assert predict_response.status_code == 200
    predict_data = predict_response.get_json()

    assert len(predict_data['predictions']) == 7
    assert 'model_accuracy' in predict_data
    assert 'meets_accuracy_threshold' in predict_data
    assert 'best_model' in predict_data

    # 4. Test trends
    trends_response = client.get('/api/analytics/trends?period=monthly', headers=headers)
    assert trends_response.status_code == 200
    trends_data = trends_response.get_json()
    assert len(trends_data['trends']) > 0

    # 5. Test category analysis
    category_response = client.get('/api/analytics/category-analysis', headers=headers)
    assert category_response.status_code == 200
    category_data = category_response.get_json()
    assert len(category_data['category_analysis']) > 0

    # Verify categories are present
    categories = [item['category'] for item in category_data['category_analysis']]
    assert 'Food' in categories
    assert 'Transport' in categories


def test_error_handling_integration(client):
    """Test error handling across the application"""

    # Test unauthenticated access
    response = client.get('/api/expenses/')
    assert response.status_code == 401

    response = client.post('/api/expenses/', json={'amount': 50})
    assert response.status_code == 401

    # Test invalid data
    # First register and login
    client.post('/api/auth/register', json={
        'username': 'error_test_user',
        'email': 'error@example.com',
        'password': 'ErrorPass123'
    })

    login = client.post('/api/auth/login', json={
        'username': 'error_test_user',
        'password': 'ErrorPass123'
    })
    token = login.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Test invalid expense creation
    response = client.post('/api/expenses/', json={
        'amount': 'invalid_amount',  # Should be number
        'category': 'Food'
    }, headers=headers)
    assert response.status_code == 400

    # Test accessing non-existent expense
    response = client.get('/api/expenses/99999', headers=headers)
    assert response.status_code == 404

    # Test updating non-existent expense
    response = client.put('/api/expenses/99999', json={
        'amount': 100
    }, headers=headers)
    assert response.status_code == 404

    # Test deleting non-existent expense
    response = client.delete('/api/expenses/99999', headers=headers)
    assert response.status_code == 404

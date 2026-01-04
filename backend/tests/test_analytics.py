import pytest
from app import app, db
from models.user import User
from models.expense import Expense
from services.prediction_service import predict_expenses
from datetime import datetime, timedelta


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


@pytest.fixture
def sample_expenses():
    """Create sample expense data for testing"""
    base_date = datetime(2025, 1, 1)
    expenses = []

    # Create 15 sample expenses with increasing amounts
    for i in range(15):
        expense = Expense(
            user_id=1,
            amount=50.0 + i * 5,  # 50, 55, 60, ..., 120
            category='Food',
            description=f'Test expense {i+1}',
            transaction_type='expense',
            date=base_date + timedelta(days=i)
        )
        expenses.append(expense)

    return expenses


def test_predict_insufficient_data(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}

    response = client.get('/api/analytics/predict?days=7', headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Not enough data' in data['error']


def test_predict_with_data(client, auth_token, sample_expenses):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Add sample expenses to database
    with app.app_context():
        for expense in sample_expenses:
            db.session.add(expense)
        db.session.commit()

    response = client.get('/api/analytics/predict?days=7', headers=headers)
    assert response.status_code == 200
    data = response.get_json()

    # Check response structure
    assert 'predictions' in data
    assert 'total_predicted' in data
    assert 'average_per_day' in data
    assert 'model_accuracy' in data
    assert 'meets_accuracy_threshold' in data
    assert 'best_model' in data
    assert 'model_details' in data

    # Check predictions array
    assert len(data['predictions']) == 7
    for prediction in data['predictions']:
        assert 'date' in prediction
        assert 'predicted_amount' in prediction
        assert prediction['predicted_amount'] >= 0

    # Check accuracy metrics
    assert isinstance(data['model_accuracy'], float)
    assert 0 <= data['model_accuracy'] <= 1
    assert isinstance(data['meets_accuracy_threshold'], bool)


def test_get_trends(client, auth_token, sample_expenses):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Add sample expenses to database
    with app.app_context():
        for expense in sample_expenses:
            db.session.add(expense)
        db.session.commit()

    response = client.get('/api/analytics/trends?period=monthly', headers=headers)
    assert response.status_code == 200
    data = response.get_json()

    assert 'trends' in data
    assert isinstance(data['trends'], list)
    assert len(data['trends']) > 0

    # Check trend structure
    for trend in data['trends']:
        assert 'period' in trend
        assert 'income' in trend
        assert 'expense' in trend
        assert 'net' in trend


def test_get_category_analysis(client, auth_token, sample_expenses):
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Add sample expenses to database
    with app.app_context():
        for expense in sample_expenses:
            db.session.add(expense)
        db.session.commit()

    response = client.get('/api/analytics/category-analysis', headers=headers)
    assert response.status_code == 200
    data = response.get_json()

    assert 'category_analysis' in data
    assert isinstance(data['category_analysis'], list)
    assert len(data['category_analysis']) > 0

    # Check analysis structure
    for analysis in data['category_analysis']:
        assert 'category' in analysis
        assert 'transaction_type' in analysis
        assert 'count' in analysis
        assert 'total' in analysis
        assert 'average' in analysis


def test_prediction_service_insufficient_data():
    """Test prediction service with insufficient data"""
    result = predict_expenses([])
    assert 'error' in result
    assert 'Insufficient data' in result['error']


def test_prediction_service_with_data(sample_expenses):
    """Test prediction service directly with sample data"""
    result = predict_expenses(sample_expenses, days=5)

    # Check basic structure
    assert 'predictions' in result
    assert 'total_predicted' in result
    assert 'model_accuracy' in result
    assert 'meets_accuracy_threshold' in result
    assert 'best_model' in result

    # Check predictions
    assert len(result['predictions']) == 5
    for pred in result['predictions']:
        assert 'date' in pred
        assert 'predicted_amount' in pred
        assert isinstance(pred['predicted_amount'], float)

    # Check accuracy
    assert isinstance(result['model_accuracy'], float)
    assert 0 <= result['model_accuracy'] <= 1
    assert isinstance(result['meets_accuracy_threshold'], bool)

    # Check model details
    assert 'model_details' in result
    assert isinstance(result['model_details'], dict)


def test_prediction_service_model_selection(sample_expenses):
    """Test that the service selects the best performing model"""
    result = predict_expenses(sample_expenses)

    # Should select one of the available models
    assert result['best_model'] in ['linear_regression', 'random_forest']

    # Model details should contain both models
    assert 'linear_regression' in result['model_details']
    assert 'random_forest' in result['model_details']

    # Each model should have accuracy metrics
    for model_name in ['linear_regression', 'random_forest']:
        model_data = result['model_details'][model_name]
        assert 'r2_score' in model_data
        assert 'mae' in model_data
        assert 'rmse' in model_data


def test_analytics_unauthorized_access(client):
    """Test that analytics endpoints require authentication"""
    response = client.get('/api/analytics/predict?days=7')
    assert response.status_code == 401

    response = client.get('/api/analytics/trends')
    assert response.status_code == 401

    response = client.get('/api/analytics/category-analysis')
    assert response.status_code == 401

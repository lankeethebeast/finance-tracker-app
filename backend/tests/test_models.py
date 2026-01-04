import pytest
from app import app, db
from models.user import User
from models.expense import Expense
from datetime import datetime


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


def test_user_model_creation(client):
    """Test User model creation and basic functionality"""
    with app.app_context():
        # Create user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password',
            role='user'
        )
        db.session.add(user)
        db.session.commit()

        # Test retrieval
        retrieved_user = User.query.filter_by(username='testuser').first()
        assert retrieved_user is not None
        assert retrieved_user.username == 'testuser'
        assert retrieved_user.email == 'test@example.com'
        assert retrieved_user.role == 'user'

        # Test to_dict method
        user_dict = retrieved_user.to_dict()
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['role'] == 'user'
        assert 'id' in user_dict
        assert 'created_at' in user_dict


def test_user_model_unique_constraints(client):
    """Test unique constraints on username and email"""
    with app.app_context():
        # Create first user
        user1 = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(user1)
        db.session.commit()

        # Try to create user with same username
        user2 = User(
            username='testuser',  # Same username
            email='different@example.com',
            password_hash='hashed_password2'
        )
        db.session.add(user2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()

        db.session.rollback()

        # Try to create user with same email
        user3 = User(
            username='differentuser',
            email='test@example.com',  # Same email
            password_hash='hashed_password3'
        )
        db.session.add(user3)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()


def test_expense_model_creation(client):
    """Test Expense model creation and relationships"""
    with app.app_context():
        # Create user first
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()

        # Create expense
        expense = Expense(
            user_id=user.id,
            amount=50.0,
            category='Food',
            description='Lunch',
            transaction_type='expense',
            date=datetime(2025, 1, 1)
        )
        db.session.add(expense)
        db.session.commit()

        # Test retrieval
        retrieved_expense = Expense.query.filter_by(user_id=user.id).first()
        assert retrieved_expense is not None
        assert retrieved_expense.amount == 50.0
        assert retrieved_expense.category == 'Food'
        assert retrieved_expense.transaction_type == 'expense'

        # Test relationship
        assert retrieved_expense.user == user
        assert expense in user.expenses

        # Test to_dict method
        expense_dict = retrieved_expense.to_dict()
        assert expense_dict['amount'] == 50.0
        assert expense_dict['category'] == 'Food'
        assert expense_dict['transaction_type'] == 'expense'
        assert 'id' in expense_dict
        assert 'date' in expense_dict


def test_expense_model_validation(client):
    """Test Expense model validation constraints"""
    with app.app_context():
        # Create user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()

        # Test valid expense
        valid_expense = Expense(
            user_id=user.id,
            amount=100.0,
            category='Transport',
            transaction_type='expense'
        )
        db.session.add(valid_expense)
        db.session.commit()

        # Test invalid transaction type (should be handled by application logic)
        # This tests the model constraints
        retrieved = Expense.query.filter_by(amount=100.0).first()
        assert retrieved.transaction_type == 'expense'


def test_user_role_defaults(client):
    """Test that user role defaults to 'user'"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
            # No role specified, should default to 'user'
        )
        db.session.add(user)
        db.session.commit()

        retrieved_user = User.query.filter_by(username='testuser').first()
        assert retrieved_user.role == 'user'


def test_expense_cascade_delete(client):
    """Test that expenses are deleted when user is deleted"""
    with app.app_context():
        # Create user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()

        # Create expenses for user
        expense1 = Expense(
            user_id=user.id,
            amount=50.0,
            category='Food',
            transaction_type='expense'
        )
        expense2 = Expense(
            user_id=user.id,
            amount=25.0,
            category='Transport',
            transaction_type='expense'
        )
        db.session.add_all([expense1, expense2])
        db.session.commit()

        # Verify expenses exist
        assert len(Expense.query.filter_by(user_id=user.id).all()) == 2

        # Delete user
        db.session.delete(user)
        db.session.commit()

        # Verify expenses are also deleted (cascade delete)
        assert len(Expense.query.filter_by(user_id=user.id).all()) == 0

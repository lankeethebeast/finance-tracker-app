from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.expense import Expense
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def validate_expense_data(data):
    """Validate expense data"""
    if not data:
        return False, "No data provided"

    required_fields = ['amount', 'category', 'transaction_type']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Validate amount
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return False, "Amount must be greater than 0"
        if amount > 1000000:  # Reasonable upper limit
            return False, "Amount exceeds maximum allowed value"
    except (ValueError, TypeError):
        return False, "Invalid amount format"

    # Validate transaction type
    if data['transaction_type'] not in ['income', 'expense']:
        return False, "Transaction type must be 'income' or 'expense'"

    # Validate category
    if not data['category'] or len(data['category'].strip()) == 0:
        return False, "Category cannot be empty"
    if len(data['category']) > 100:
        return False, "Category name too long"

    # Validate description (optional)
    if 'description' in data and len(data['description']) > 500:
        return False, "Description too long"

    return True, "Valid"

bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    user_id = int(get_jwt_identity())

    category = request.args.get('category')
    transaction_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Expense.query.filter_by(user_id=user_id)

    if category:
        query = query.filter_by(category=category)
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    if start_date:
        query = query.filter(Expense.date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Expense.date <= datetime.fromisoformat(end_date))

    expenses = query.order_by(Expense.date.desc()).all()

    return jsonify({'expenses': [expense.to_dict() for expense in expenses]}), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_expense():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        logger.info(f"Creating expense for user {user_id}")

        # Validate expense data
        is_valid, validation_msg = validate_expense_data(data)
        if not is_valid:
            logger.warning(f"Invalid expense data for user {user_id}: {validation_msg}")
            return jsonify({'error': validation_msg}), 400

        # Parse date
        if data.get('date'):
            try:
                # Handle both date-only (YYYY-MM-DD) and datetime formats
                expense_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                try:
                    # If it's just a date string, parse it as such
                    expense_date = datetime.strptime(data['date'], '%Y-%m-%d')
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        else:
            expense_date = datetime.utcnow()

        new_expense = Expense(
            user_id=user_id,
            amount=float(data['amount']),
            category=data['category'].strip(),
            description=data.get('description', '').strip(),
            transaction_type=data['transaction_type'],
            date=expense_date
        )

        db.session.add(new_expense)
        db.session.commit()

        logger.info(f"Expense created successfully: ID {new_expense.id} for user {user_id}")
        return jsonify({'message': 'Expense created successfully', 'expense': new_expense.to_dict()}), 201

    except Exception as e:
        logger.error(f"Error creating expense for user {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create expense'}), 500

@bp.route('/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    user_id = int(get_jwt_identity())
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    return jsonify({'expense': expense.to_dict()}), 200

@bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    user_id = int(get_jwt_identity())
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    data = request.get_json()

    if data.get('amount'):
        expense.amount = float(data['amount'])
    if data.get('category'):
        expense.category = data['category']
    if data.get('description') is not None:
        expense.description = data['description']
    if data.get('transaction_type'):
        if data['transaction_type'] not in ['income', 'expense']:
            return jsonify({'error': 'Invalid transaction type'}), 400
        expense.transaction_type = data['transaction_type']
    if data.get('date'):
        expense.date = datetime.fromisoformat(data['date'])

    db.session.commit()

    return jsonify({'message': 'Expense updated successfully', 'expense': expense.to_dict()}), 200

@bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = int(get_jwt_identity())
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({'message': 'Expense deleted successfully'}), 200

@bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    user_id = int(get_jwt_identity())

    total_income = db.session.query(db.func.sum(Expense.amount)).filter_by(
        user_id=user_id, transaction_type='income'
    ).scalar() or 0

    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(
        user_id=user_id, transaction_type='expense'
    ).scalar() or 0

    balance = total_income - total_expenses

    category_breakdown = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount).label('total')
    ).filter_by(
        user_id=user_id, transaction_type='expense'
    ).group_by(Expense.category).all()

    return jsonify({
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'balance': float(balance),
        'category_breakdown': [{'category': cat, 'total': float(total)} for cat, total in category_breakdown]
    }), 200

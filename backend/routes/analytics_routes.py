from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.prediction_service import predict_expenses
from models.expense import Expense
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@bp.route('/predict', methods=['GET'])
@jwt_required()
def get_predictions():
    user_id = int(get_jwt_identity())

    days = request.args.get('days', default=30, type=int)

    # Validate days parameter
    if days < 1 or days > 365:
        return jsonify({'error': 'Days must be between 1 and 365'}), 400

    expenses = Expense.query.filter_by(user_id=user_id, transaction_type='expense').order_by(Expense.date).all()

    logger.info(f"Prediction request for user {user_id}: {len(expenses)} expenses, {days} days")

    if len(expenses) < 10:
        logger.warning(f"Insufficient data for prediction: user {user_id} has only {len(expenses)} expenses")
        return jsonify({'error': 'Not enough data for prediction. Need at least 10 transactions.'}), 400

    try:
        predictions = predict_expenses(expenses, days)
        logger.info(f"Prediction completed for user {user_id}")
        return jsonify(predictions), 200
    except Exception as e:
        logger.error(f"Prediction failed for user {user_id}: {str(e)}")
        return jsonify({'error': 'Prediction calculation failed'}), 500

@bp.route('/trends', methods=['GET'])
@jwt_required()
def get_trends():
    user_id = int(get_jwt_identity())

    period = request.args.get('period', default='monthly')

    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date).all()

    if not expenses:
        return jsonify({'trends': []}), 200

    trends_data = []

    if period == 'daily':
        date_format = '%Y-%m-%d'
    elif period == 'weekly':
        date_format = '%Y-W%W'
    else:
        date_format = '%Y-%m'

    from collections import defaultdict
    grouped = defaultdict(lambda: {'income': 0, 'expense': 0})

    for expense in expenses:
        period_key = expense.date.strftime(date_format)
        if expense.transaction_type == 'income':
            grouped[period_key]['income'] += expense.amount
        else:
            grouped[period_key]['expense'] += expense.amount

    for period_key, amounts in sorted(grouped.items()):
        trends_data.append({
            'period': period_key,
            'income': amounts['income'],
            'expense': amounts['expense'],
            'net': amounts['income'] - amounts['expense']
        })

    return jsonify({'trends': trends_data}), 200

@bp.route('/category-analysis', methods=['GET'])
@jwt_required()
def get_category_analysis():
    user_id = int(get_jwt_identity())

    from extensions import db

    category_stats = db.session.query(
        Expense.category,
        Expense.transaction_type,
        db.func.count(Expense.id).label('count'),
        db.func.sum(Expense.amount).label('total'),
        db.func.avg(Expense.amount).label('average')
    ).filter_by(user_id=user_id).group_by(
        Expense.category, Expense.transaction_type
    ).all()

    analysis = []
    for cat, trans_type, count, total, avg in category_stats:
        analysis.append({
            'category': cat,
            'transaction_type': trans_type,
            'count': count,
            'total': float(total),
            'average': float(avg)
        })

    return jsonify({'category_analysis': analysis}), 200

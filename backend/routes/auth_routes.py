from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from extensions import db, bcrypt
from models.user import User
import re
import logging

logger = logging.getLogger(__name__)

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_username(username):
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 50:
        return False, "Username must be less than 50 characters long"
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    return True, "Username is valid"

def role_required(required_role):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            if user.role != required_role and user.role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        logger.warning("Registration attempt with missing required fields")
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate username
    username_valid, username_msg = validate_username(data['username'])
    if not username_valid:
        return jsonify({'error': username_msg}), 400

    # Validate email
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400

    # Validate password
    password_valid, password_msg = validate_password(data['password'])
    if not password_valid:
        return jsonify({'error': password_msg}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Check if role is provided and valid
    role = data.get('role', 'user')
    if role not in ['user', 'admin']:
        return jsonify({'error': 'Invalid role. Must be user or admin'}), 400

    # Only allow admin role if there are no existing users (first user) or if current user is admin
    if role == 'admin':
        # Check if this is the first user
        if User.query.count() > 0:
            # For non-first users, require admin authentication
            current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
            if not current_user_id:
                return jsonify({'error': 'Admin role requires authentication'}), 403
            current_user = User.query.get(current_user_id)
            if not current_user or current_user.role != 'admin':
                return jsonify({'error': 'Only admins can create admin accounts'}), 403

    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=password_hash,
        role=role
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New user registered: {data['username']} with role: {role}")
        return jsonify({'message': 'User registered successfully', 'user': new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering user {data['username']}: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        logger.warning("Login attempt with missing credentials")
        return jsonify({'error': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        logger.warning(f"Failed login attempt for username: {data.get('username', 'unknown')}")
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=str(user.id))
    logger.info(f"Successful login for user: {user.username}")

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict()}), 200

@bp.route('/users', methods=['GET'])
@role_required('admin')
def get_all_users():
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200

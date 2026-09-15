"""
Authentication routes for user registration, login, and logout.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError, validate

from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Schema for validation
class UserRegisterSchema(Schema):
    """Schema for user registration validation."""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=120),
        error_messages={'required': 'Username is required'}
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6),
        error_messages={'required': 'Password is required', 'validator_failed': 'Password must be at least 6 characters'}
    )

class UserLoginSchema(Schema):
    """Schema for user login validation."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request body:
    {
        "username": "string",
        "email": "email",
        "password": "string (min 6 chars)"
    }
    
    Returns:
    - 201: User created successfully
    - 400: Validation error or user already exists
    """
    try:
        data = register_schema.load(request.get_json())
    except ValidationError as err:
        return {'errors': err.messages}, 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return {'error': 'Username already exists'}, 400
    
    if User.query.filter_by(email=data['email']).first():
        return {'error': 'Email already exists'}, 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return {
            'message': 'User created successfully',
            'user': user.to_dict()
        }, 201
    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to create user', 'details': str(e)}, 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login a user and return a JWT token.
    
    Request body:
    {
        "email": "email",
        "password": "string"
    }
    
    Returns:
    - 200: Login successful with access token
    - 400: Validation error
    - 401: Invalid credentials
    """
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return {'errors': err.messages}, 400
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return {'error': 'Invalid email or password'}, 401
    
    # Create JWT token
    access_token = create_access_token(identity=user.id)
    
    return {
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }, 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get the current user's profile.
    
    Returns:
    - 200: User profile data
    - 401: Unauthorized
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    if not user:
        return {'error': 'User not found'}, 404
    
    return {
        'user': user.to_dict()
    }, 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout a user (JWT token invalidation is handled client-side).
    
    Returns:
    - 200: Logout successful
    """
    return {'message': 'Logout successful'}, 200

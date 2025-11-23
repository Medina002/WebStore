from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.extensions import db
from app.models import User

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (Admin only)"""
    claims = get_jwt()
    role = claims.get('role')
    
    if role != 'admin':
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get single user (Admin only)"""
    claims = get_jwt()
    role = claims.get('role')
    
    if role != 'admin':
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user (Admin only)"""
    claims = get_jwt()
    role = claims.get('role')
    
    if role != 'admin':
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        valid_roles = ['admin', 'advanced_user', 'simple_user']
        if data['role'] in valid_roles:
            user.role = data['role']
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200

@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user (Admin only)"""
    claims = get_jwt()
    role = claims.get('role')
    
    if role != 'admin':
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    current_user_id = get_jwt_identity()
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200
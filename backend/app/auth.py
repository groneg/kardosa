from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime
from .models import User, Token

def token_required(f):
    """Decorator to verify UUID token in Authorization header"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token_str = None
        
        # Check if Authorization header exists and has the correct format
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token_str = auth_header.split(' ')[1]
        
        # Initialize token_user to None (will be passed to the decorated function)
        token_user = None
        
        # If token is provided, try to authenticate with it
        if token_str:
            # Find the token in the database
            token = Token.query.filter_by(token=token_str).first()
            
            # Verify token exists and is not expired
            if token and token.expiration > datetime.utcnow() and not token.is_revoked:
                token_user = User.query.get(token.user_id)
                if not token_user:
                    return jsonify({'error': 'Invalid token - user not found'}), 401
            elif token and token.expiration <= datetime.utcnow():
                return jsonify({'error': 'Token has expired'}), 401
            elif token and token.is_revoked:
                return jsonify({'error': 'Token has been revoked'}), 401
            else:
                return jsonify({'error': 'Invalid token'}), 401
        
        # Check if the user is authenticated via Flask-Login (fallback)
        from flask_login import current_user as flask_login_user
        if not token_user and not flask_login_user.is_authenticated:
            # No valid authentication - either via token or cookies
            return jsonify({'error': 'Authentication required'}), 401
            
        # Use token user if available, otherwise use Flask-Login user
        authenticated_user = token_user if token_user else flask_login_user
            
        # Pass the authenticated user to the decorated function
        return f(current_user=authenticated_user, *args, **kwargs)
    
    return decorated

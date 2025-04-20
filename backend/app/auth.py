from functools import wraps
from flask import request, jsonify, current_app
import jwt
from .models import User

def token_required(f):
    """Decorator to verify JWT token in Authorization header"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if Authorization header exists and has the correct format
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Initialize current_user to None (will be passed to the decorated function)
        jwt_user = None
        
        # If token is provided, try to authenticate with it
        if token:
            try:
                # Decode the token
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                jwt_user = User.query.get(data['user_id'])
                
                if not jwt_user:
                    return jsonify({'error': 'Invalid token - user not found'}), 401
                
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
        
        # Check if the user is authenticated via Flask-Login
        from flask_login import current_user as flask_login_user
        if not jwt_user and not flask_login_user.is_authenticated:
            # No valid authentication - either via JWT or cookies
            return jsonify({'error': 'Authentication required'}), 401
            
        # Use JWT user if available, otherwise use Flask-Login user
        authenticated_user = jwt_user if jwt_user else flask_login_user
            
        # Pass the authenticated user to the decorated function
        return f(current_user=authenticated_user, *args, **kwargs)
    
    return decorated

"""
API Key Authentication for CareQueue.

This module provides authentication middleware for protecting doctor endpoints.
Doctors must provide their API key in the 'x-api-key' header to access
protected endpoints like completing tokens.
"""

from functools import wraps
from flask import request, jsonify
from models import Doctor


def require_api_key(f):
    """
    Decorator to require API key authentication for doctor endpoints.
    
    Usage:
        @app.route('/protected-endpoint', methods=['POST'])
        @require_api_key
        def protected_function():
            # This code only runs if API key is valid
            # Access the authenticated doctor via request.doctor
            return jsonify({'message': 'Success'})
    
    How it works:
    1. Extracts 'x-api-key' from request headers
    2. Validates the key against the doctors table
    3. If valid, adds the doctor object to request.doctor
    4. If invalid or missing, returns 401/403 error
    
    Args:
        f: The function to wrap
        
    Returns:
        Wrapped function with API key validation
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract API key from header
        api_key = request.headers.get('x-api-key')
        
        if not api_key:
            # No API key provided
            return jsonify({
                'error': 'API key is required',
                'message': 'Please provide x-api-key header'
            }), 401
        
        # Validate API key against database
        doctor = Doctor.query.filter_by(api_key=api_key).first()
        
        if not doctor:
            # Invalid API key
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key does not match any doctor'
            }), 403
        
        # API key is valid - attach doctor to request object
        # The protected endpoint can access this via request.doctor
        request.doctor = doctor
        
        # Call the original function
        return f(*args, **kwargs)
    
    return decorated_function

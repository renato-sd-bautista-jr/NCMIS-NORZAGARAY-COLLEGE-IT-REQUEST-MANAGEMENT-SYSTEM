from functools import wraps
from flask import session, redirect, url_for, abort


def check_permission(feature, action):
    """
    Decorator to check if the current user has permission for a specific feature and action.
    
    Args:
        feature (str): The feature name (e.g., 'damage_report', 'inventory', 'dashboard')
        action (str): The action type (e.g., 'view', 'edit')
    
    Returns:
        function: Decorated function that checks permissions before executing
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            user = session.get('user')
            if not user:
                return redirect(url_for('login_bp.login'))
            
            # Admin users bypass permission checks
            if user.get('is_admin'):
                return f(*args, **kwargs)
            
            # Get permissions from session
            permissions = user.get('permissions', {})
            
            # Check if the feature exists in permissions
            if feature not in permissions:
                abort(403)
            
            # Check if the action is permitted for this feature
            feature_perms = permissions.get(feature, {})
            if not isinstance(feature_perms, dict):
                abort(403)
            
            # Check specific action permission
            if not feature_perms.get(action, False):
                abort(403)
            
            # Permission granted, execute the function
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

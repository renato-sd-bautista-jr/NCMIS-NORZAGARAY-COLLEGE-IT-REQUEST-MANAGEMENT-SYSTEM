from functools import wraps
from datetime import datetime, timedelta
from flask import session, redirect, url_for, request, flash, jsonify, current_app

DEFAULT_IDLE_TIMEOUT_SECONDS = 3600

EXEMPT_ENDPOINTS = {
    'login_bp.login',
    'login_bp.logout',
    'login_bp.qrcode_generator_page',
    'static',
}

EXEMPT_PATH_PREFIXES = [
    '/static/',
    '/favicon.ico',
    '/robots.txt',
]


def is_authenticated() -> bool:
    return bool(session.get('user'))


def clear_user_session():
    session.pop('user', None)
    session.pop('last_activity', None)


def get_idle_timeout_seconds() -> int:
    return int(current_app.config.get('IDLE_TIMEOUT_SECONDS', DEFAULT_IDLE_TIMEOUT_SECONDS))


def has_session_timed_out() -> bool:
    last_activity = session.get('last_activity')
    if last_activity is None:
        return False

    try:
        last_activity = float(last_activity)
    except (TypeError, ValueError):
        return False

    return (datetime.utcnow().timestamp() - last_activity) > get_idle_timeout_seconds()


def update_last_activity() -> None:
    session.permanent = True
    session['last_activity'] = datetime.utcnow().timestamp()


def should_skip_auth() -> bool:
    endpoint = request.endpoint or ''
    if endpoint in EXEMPT_ENDPOINTS:
        return True

    path = request.path or ''
    if any(path.startswith(prefix) for prefix in EXEMPT_PATH_PREFIXES):
        return True

    return False


def _unauthorized_response():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in (request.headers.get('Accept') or ''):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    flash('Please sign in to continue.', 'error')
    return redirect(url_for('login_bp.login'))


def _session_timeout_response():
    clear_user_session()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in (request.headers.get('Accept') or ''):
        return jsonify({'success': False, 'message': 'Session expired due to inactivity'}), 401
    flash('Your session has expired due to inactivity. Please log in again.', 'error')
    return redirect(url_for('login_bp.login'))


def enforce_login():
    if should_skip_auth():
        return None

    if not is_authenticated():
        return _unauthorized_response()

    if has_session_timed_out():
        return _session_timeout_response()

    update_last_activity()
    return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = enforce_login()
        if result is not None:
            return result
        return f(*args, **kwargs)
    return decorated_function


def init_auth(app):
    app.config.setdefault('IDLE_TIMEOUT_SECONDS', DEFAULT_IDLE_TIMEOUT_SECONDS)
    app.config.setdefault('PERMANENT_SESSION_LIFETIME', timedelta(hours=1))
    app.before_request(lambda: enforce_login())

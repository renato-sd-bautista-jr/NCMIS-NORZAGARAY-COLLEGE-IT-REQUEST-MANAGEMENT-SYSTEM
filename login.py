from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db_connection
import bcrypt,json
from datetime import datetime

# Blueprint setup
login_bp = Blueprint('login_bp', __name__, url_prefix='/login')


# =============================
# LOGIN ROUTE
# =============================
@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT user_id, username, is_admin, password, permissions FROM users WHERE username=%s",
                    (username,)
                )
                user = cursor.fetchone()
        finally:
            conn.close()

        # Username not found
        if not user:
            flash("Invalid username. Please try again.", "error")
            return redirect(url_for('login_bp.login'))

        # Wrong password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            flash("Incorrect password. Please try again.", "error")
            return redirect(url_for('login_bp.login'))

        # Decode permissions JSON safely
        import json
        permissions = {}
        if user.get('permissions'):
            try:
                permissions = json.loads(user['permissions'])
            except json.JSONDecodeError:
                permissions = {}

        # Save session data
        session['user'] = {
            'user_id': user['user_id'],
            'username': user['username'],
            'is_admin': bool(user['is_admin']),
            'permissions': permissions
        }

        
        return redirect(url_for('dashboard_bp.dashboard_load'))
        # ✅ Handle GET requests here
    return render_template('login.html')


# =============================
# LOGOUT ROUTE
# =============================
@login_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login_bp.login'))


# =============================
# LOGIN PAGE (DIRECT ROUTE)
# =============================
@login_bp.route('/login-page')
def qrcode_generator_page():
    """Render login page directly"""
    return render_template('login.html')


# =============================
# MAIN ROUTE (USER DASHBOARD)
# =============================
def main():
    """Main user page after login"""
    if 'user_id' not in session:
        return redirect(url_for('login_bp.login'))
    
    if session.get('is_admin'):
        return redirect(url_for('admin'))

    from userborrow import get_available_devices, get_available_units
    raw_items = get_available_devices()

    items = [
        {
            'id': i['id'],
            'name': i['name'],
            'serial_number': i['serial_number'],
            'department': i['department']
        }
        for i in raw_items
    ]

    units = get_available_units()

    return render_template(
        'main.html',
        username=session.get('username'),
        items=items,
        units=units
    )

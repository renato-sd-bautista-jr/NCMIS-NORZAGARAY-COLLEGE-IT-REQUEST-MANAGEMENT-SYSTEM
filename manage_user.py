import pymysql
from db import get_db_connection
from flask import Blueprint, jsonify, request, render_template, redirect, url_for

manage_user_bp = Blueprint('manage_user_bp', __name__, template_folder='templates')


# ========================
# LOAD MANAGE USERS PAGE
# ========================
@manage_user_bp.route('/manage-user')
def manage_user_page():
    """
    Load Manage Users page and display all users.
    """
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    user_id,
                    username,
                    faculty_name,
                    email,
                    is_admin,
                    is_active,
                    created_at
                FROM users
                ORDER BY faculty_name
            """)
            users = cursor.fetchall()
        return render_template('manage_user.html', users=users)
    finally:
        conn.close()


# ========================
# GET USERS (JSON)
# ========================
@manage_user_bp.route('/get-users')
def get_users():
    """
    Fetch all users (for API/AJAX use).
    """
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    user_id,
                    username,
                    faculty_name,
                    email,
                    is_admin,
                    is_active,
                    created_at,
                    updated_at
                FROM users
                ORDER BY faculty_name
            """)
            users = cursor.fetchall()
            return jsonify(users)
    finally:
        conn.close()


# ========================
# ADD OR UPDATE USER
# ========================
@manage_user_bp.route('/add-or-update-user', methods=['POST'])
def add_or_update_user():
    """
    Add a new user or update an existing one.
    """
    data = request.form
    user_id = data.get('user_id')
    faculty_name = data.get('faculty_name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_admin = int(data.get('is_admin', 0))

    if not faculty_name or not username or not email:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if user_id:  # Update existing user
                sql = """
                    UPDATE users
                    SET faculty_name=%s, username=%s, email=%s, is_admin=%s, updated_at=NOW()
                    WHERE user_id=%s
                """
                cursor.execute(sql, (faculty_name, username, email, is_admin, user_id))
            else:  # Add new user
                sql = """
                    INSERT INTO users (faculty_name, username, email, password, is_admin, is_active, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, 1, NOW(), NOW())
                """
                cursor.execute(sql, (faculty_name, username, email, password, is_admin))
        conn.commit()
        return redirect(url_for('manage_user_bp.manage_user_page'))
    finally:
        conn.close()


# ========================
# DEACTIVATE USER
# ========================
@manage_user_bp.route('/deactivate-user', methods=['POST'])
def deactivate_user():
    """
    Soft deactivate a user (set is_active = 0)
    """
    user_id = request.form.get('user_id')

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET is_active = 0, updated_at = NOW() WHERE user_id = %s", (user_id,))
        conn.commit()
        return redirect(url_for('manage_user_bp.manage_user_page'))
    finally:
        conn.close()


# ========================
# ACTIVATE USER
# ========================
@manage_user_bp.route('/activate-user', methods=['POST'])
def activate_user():
    """
    Reactivate a user (set is_active = 1)
    """
    user_id = request.form.get('user_id')

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET is_active = 1, updated_at = NOW() WHERE user_id = %s", (user_id,))
        conn.commit()
        return redirect(url_for('manage_user_bp.manage_user_page'))
    finally:
        conn.close()


# ========================
# EDIT USER (Placeholder)
# ========================
@manage_user_bp.route('/edit-user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    return f"Edit user {id}"

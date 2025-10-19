import pymysql
from db import get_db_connection
from flask import Blueprint, send_file, jsonify, request, render_template, redirect, url_for

manage_user_bp = Blueprint('manage_user_bp', __name__, template_folder='templates')


@manage_user_bp.route('/manage-user')
def manage_user_page():
    """
    Load the Manage Users page and display all users.
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
                    created_at
                FROM users
                ORDER BY faculty_name
            """)
            users = cursor.fetchall()
        # Render the manage_user.html page and pass user data
        return render_template('manage_user.html', users=users)
    finally:
        conn.close()


@manage_user_bp.route('/get-users')
def get_user():
    """
    Fetch all users from the users table (for API/AJAX use).
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
                    created_at,
                    updated_at
                FROM users
                ORDER BY faculty_name
            """)
            users = cursor.fetchall()
            return jsonify(users)
    finally:
        conn.close()


@manage_user_bp.route('/edit-user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    return f"Edit user {id}"


@manage_user_bp.route('/delete-user/<int:id>', methods=['POST'])
def delete_user(id):
    return redirect(url_for('manage_user_bp.manage_user_page'))


@manage_user_bp.route('/add-or-update-user', methods=['POST'])
def add_or_update_user():
    data = request.form
    user_id = data.get('user_id')
    faculty_name = data.get('faculty_name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if user_id:  # Update
                sql = """
                    UPDATE users
                    SET faculty_name=%s, username=%s, email=%s, is_admin=%s, updated_at=NOW()
                    WHERE user_id=%s
                """
                cursor.execute(sql, (faculty_name, username, email, is_admin, user_id))
            else:  # Insert
                sql = """
                    INSERT INTO users (faculty_name, username, email, password, is_admin, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """
                cursor.execute(sql, (faculty_name, username, email, password, is_admin))
        conn.commit()
        return redirect(url_for('manage_user_bp.manage_user_page'))
    finally:
        conn.close()

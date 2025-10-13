import pymysql
from db import get_db_connection
from flask import Blueprint, send_file, jsonify, request, render_template

manage_user_bp = Blueprint('manage_user_bp', __name__, template_folder='templates')


@manage_user_bp.route('/get-users')
def get_user():
    """
    Fetch all users from the users table with the necessary columns.
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
            return cursor.fetchall()
    finally:
        conn.close()

@manage_user_bp.route('/edit-user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    return f"Edit user {id}"

@manage_user_bp.route('/delete-user/<int:id>', methods=['POST'])
def delete_user(id):
    return redirect(url_for('users'))     
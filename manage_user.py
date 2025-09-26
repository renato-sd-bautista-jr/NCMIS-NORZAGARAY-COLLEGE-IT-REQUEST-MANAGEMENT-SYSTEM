import pymysql
from db import get_db_connection

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


def edit_user(id):
    return f"Edit user {id}"


def delete_user(id):
    return redirect(url_for('users'))     
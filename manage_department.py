import pymysql
from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection

manage_department_bp = Blueprint('manage_department_bp', __name__, template_folder='templates')

# -----------------------------
# LOAD DEPARTMENT PAGE
# -----------------------------
@manage_department_bp.route('/manage-department')
def manage_department_page():
    return render_template('manage_department.html')


# -----------------------------
# FETCH ALL DEPARTMENTS (AJAX)
# -----------------------------
@manage_department_bp.route('/get-departments')
def get_departments():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return jsonify(cursor.fetchall())
    finally:
        conn.close()


# -----------------------------
# ADD NEW DEPARTMENT (AJAX)
# -----------------------------
@manage_department_bp.route('/add-department', methods=['POST'])
def add_department():
    data = request.get_json()
    department_name = data.get('department_name')

    if not department_name:
        return jsonify({'error': 'Department name is required'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO departments (department_name) VALUES (%s)", (department_name,))
            conn.commit()
        return jsonify({'message': 'Department added successfully'})
    finally:
        conn.close()


# -----------------------------
# UPDATE DEPARTMENT (AJAX)
# -----------------------------
@manage_department_bp.route('/update-department/<int:id>', methods=['PUT'])
def update_department(id):
    data = request.get_json()
    new_name = data.get('department_name')

    if not new_name:
        return jsonify({'error': 'Missing department name'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE departments SET department_name = %s WHERE department_id = %s", (new_name, id))
            conn.commit()
        return jsonify({'message': 'Department updated successfully'})
    finally:
        conn.close()


# -----------------------------
# DELETE DEPARTMENT (AJAX)
# -----------------------------
@manage_department_bp.route('/delete-department/<int:id>', methods=['DELETE'])
def delete_department(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM departments WHERE department_id = %s", (id,))
            conn.commit()
        return jsonify({'message': 'Department deleted successfully'})
    finally:
        conn.close()

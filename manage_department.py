import pymysql
from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection

manage_department_bp = Blueprint('manage_department_bp', __name__, template_folder='templates')

EXPECTED_DEPARTMENT_COLUMNS = {
    'max_pc_allowed': "ADD COLUMN max_pc_allowed INT UNSIGNED NOT NULL DEFAULT 0 AFTER category",
}


def _sync_departments_schema(conn):
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SHOW COLUMNS FROM departments")
        existing_columns = {row['Field'] for row in cursor.fetchall()}

        for column_name, alter_sql in EXPECTED_DEPARTMENT_COLUMNS.items():
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE departments {alter_sql}")


def ensure_departments_schema(conn=None):
    created_local_conn = False

    if conn is None:
        conn = get_db_connection()
        created_local_conn = True

    try:
        _sync_departments_schema(conn)
        conn.commit()
    finally:
        if created_local_conn:
            conn.close()

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
        ensure_departments_schema(conn)
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    d.department_id, 
                    d.department_name, 
                    d.category,
                    COALESCE(d.max_pc_allowed, 0) AS max_pc_allowed,
                    COALESCE(SUM(p.quantity), 0) AS pc_count
                FROM departments d
                LEFT JOIN pcinfofull p ON p.department_id = d.department_id
                GROUP BY d.department_id, d.department_name, d.category, d.max_pc_allowed
                ORDER BY d.department_name
            """)
            return jsonify(cursor.fetchall())
    finally:
        conn.close()


# -----------------------------
# FETCH PCS FOR ONE DEPARTMENT (AJAX)
# -----------------------------
@manage_department_bp.route('/get-department-pcs/<int:department_id>')
def get_department_pcs(department_id):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT
                    p.pcid,
                    p.pcname,
                    p.serial_no,
                    p.municipal_serial_no,
                    p.location,
                    p.status,
                    p.quantity
                FROM pcinfofull p
                WHERE p.department_id = %s
                ORDER BY p.pcname ASC, p.pcid ASC
            """, (department_id,))
            return jsonify(cursor.fetchall())
    finally:
        conn.close()


# -----------------------------
# ADD NEW DEPARTMENT (AJAX)
# -----------------------------
@manage_department_bp.route('/add-department', methods=['POST'])
def add_department():
    data = request.get_json(silent=True) or {}
    department_name = (data.get('department_name') or '').strip()
    category = (data.get('category') or '').strip()
    raw_max_pc_allowed = data.get('max_pc_allowed')

    try:
        max_pc_allowed = int(raw_max_pc_allowed)
    except (TypeError, ValueError):
        return jsonify({'error': 'A valid PC limit is required'}), 400

    if not department_name or not category:
        return jsonify({'error': 'Department name, category, and PC limit are required'}), 400
    if max_pc_allowed < 0:
        return jsonify({'error': 'PC limit must be 0 or higher'}), 400

    conn = get_db_connection()
    try:
        ensure_departments_schema(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO departments (department_name, category, max_pc_allowed) VALUES (%s, %s, %s)",
                (department_name, category, max_pc_allowed)
            )
            conn.commit()
        return jsonify({'message': 'Department added successfully'})
    finally:
        conn.close()
# -----------------------------
# UPDATE DEPARTMENT (AJAX)
# -----------------------------
@manage_department_bp.route('/update-department/<int:id>', methods=['PUT'])
def update_department(id):
    data = request.get_json(silent=True) or {}
    new_name = (data.get('department_name') or '').strip()
    category = (data.get('category') or '').strip()
    raw_max_pc_allowed = data.get('max_pc_allowed')

    try:
        max_pc_allowed = int(raw_max_pc_allowed)
    except (TypeError, ValueError):
        return jsonify({'error': 'A valid PC limit is required'}), 400

    if not new_name or not category:
        return jsonify({'error': 'Department name, category, and PC limit are required'}), 400
    if max_pc_allowed < 0:
        return jsonify({'error': 'PC limit must be 0 or higher'}), 400

    conn = get_db_connection()
    try:
        ensure_departments_schema(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE departments SET department_name = %s, category = %s, max_pc_allowed = %s WHERE department_id = %s",
                (new_name, category, max_pc_allowed, id)
            )
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
        return jsonify({'message': 'Office/Facility deleted successfully'})
    except pymysql.err.IntegrityError as e:
        return jsonify({'error': 'Cannot delete: this office/facility still has linked records (PCs or items). Remove them first.'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

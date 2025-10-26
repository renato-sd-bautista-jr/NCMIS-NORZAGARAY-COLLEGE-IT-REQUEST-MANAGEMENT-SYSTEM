from flask import Blueprint, jsonify, request, render_template,send_file
import pymysql
from db import get_db_connection
from io import BytesIO
import pandas as pd

report_bp = Blueprint('report_bp', __name__, template_folder='templates')


# -------------------------------
# 1️⃣ Render Report Page
# -------------------------------
@report_bp.route('/reportgenerator')
def report_generator_page():
    """Render the Report Generator HTML page."""
    return render_template('report.html')


@report_bp.route('/export-reports', methods=['GET'])
def export_reports():
    """Export filtered reports as Excel file."""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Same filters as /get-reports
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    department = request.args.get('department', '').strip()
    status = request.args.get('status', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    query = """
        SELECT 
            d.item_name AS Name,
            d.device_type AS Category,
            dept.department_name AS Department,
            '' AS Location,
            d.accountable AS Accountable,
            d.status AS Status,
            d.acquisition_cost AS `Acquisition Cost`,
            d.date_acquired AS `Date Acquired`
        FROM devices_full d
        LEFT JOIN departments dept ON dept.department_id = d.department_id

        UNION ALL

        SELECT 
            p.pcname AS Name,
            'PC' AS Category,
            dept.department_name AS Department,
            p.location AS Location,
            p.accountable AS Accountable,
            p.status AS Status,
            p.acquisition_cost AS `Acquisition Cost`,
            p.date_acquired AS `Date Acquired`
        FROM pcinfofull p
        LEFT JOIN departments dept ON dept.department_id = p.department_id
    """

    filters = []
    params = []

    if name:
        filters.append("Name LIKE %s")
        params.append(f"%{name}%")
    if category and category.lower() != "all":
        filters.append("Category = %s")
        params.append(category)
    if department and department.lower() != "all":
        filters.append("Department = %s")
        params.append(department)
    if status and status.lower() != "all":
        filters.append("Status = %s")
        params.append(status)
    if date_from:
        filters.append("`Date Acquired` >= %s")
        params.append(date_from)
    if date_to:
        filters.append("`Date Acquired` <= %s")
        params.append(date_to)

    if filters:
        query = f"SELECT * FROM ({query}) AS combined WHERE {' AND '.join(filters)}"

    query += " ORDER BY `Date Acquired` DESC"

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    # Create Excel file in memory
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        download_name="Reports.xlsx",
        as_attachment=True
    )
# -------------------------------
# 2️⃣ Get Combined Reports Data
# -------------------------------
@report_bp.route('/get-reports', methods=['GET'])
def get_reports():
    """
    Combine items from devices_full and pcinfofull into a unified report view.
    Supports filters like name, category, department, status, and date range.
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Filters
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    department = request.args.get('department', '').strip()
    status = request.args.get('status', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    # Base query combining both tables
    query = """
        SELECT 
            d.accession_id AS id,
            d.item_name AS name,
            d.device_type AS category,
            dept.department_name AS department,
            '' AS location,
            d.accountable,
            d.status,
            d.acquisition_cost,
            d.date_acquired
        FROM devices_full d
        LEFT JOIN departments dept ON dept.department_id = d.department_id

        UNION ALL

        SELECT 
            p.pcid AS id,
            p.pcname AS name,
            'PC' AS category,
            dept.department_name AS department,
            p.location,
            p.accountable,
            p.status,
            p.acquisition_cost,
            p.date_acquired
        FROM pcinfofull p
        LEFT JOIN departments dept ON dept.department_id = p.department_id
    """

    filters = []
    params = []

    # 🧩 Apply filters
    if name:
        filters.append("name LIKE %s")
        params.append(f"%{name}%")
    if category and category.lower() != "all":
        filters.append("category = %s")
        params.append(category)
    if department and department.lower() != "all":
        filters.append("department = %s")
        params.append(department)
    if status and status.lower() != "all":
        filters.append("status = %s")
        params.append(status)
    if date_from:
        filters.append("date_acquired >= %s")
        params.append(date_from)
    if date_to:
        filters.append("date_acquired <= %s")
        params.append(date_to)

    if filters:
        query = f"SELECT * FROM ({query}) AS combined WHERE {' AND '.join(filters)}"

    query += " ORDER BY date_acquired DESC"

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(data)

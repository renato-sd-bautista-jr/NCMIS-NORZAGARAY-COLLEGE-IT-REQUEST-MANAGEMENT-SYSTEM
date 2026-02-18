from flask import Blueprint, jsonify, request, render_template, send_file
import pymysql
from db import get_db_connection
from io import BytesIO
import pandas as pd
from utils.permissions import check_permission

damage_report_bp = Blueprint('damage_report_bp', __name__, template_folder='templates')


# -------------------------------
# 1️⃣ Render Damage Report Page
# -------------------------------
@damage_report_bp.route('/damage-report')
@check_permission('damage_report', 'view')
def damage_report_page():
    """Render the Damage Report HTML page."""
    return render_template('damage_report.html')


@damage_report_bp.route('/export-damage-reports', methods=['GET'])
@check_permission('damage_report', 'view')
def export_damage_reports():
    """Export filtered damage reports as Excel file."""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Same filters as /get-damage-reports
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    department = request.args.get('department', '').strip()
    severity = request.args.get('severity', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    query = """
        SELECT 
            d.item_name AS Name,
            d.device_type AS Category,
            dept.department_name AS Department,
            '' AS Location,
            d.accountable AS Accountable,
            CASE 
                WHEN d.damage_severity IS NULL OR d.damage_severity = '' THEN 'Minor'
                ELSE d.damage_severity
            END AS Severity,
            d.damage_description AS `Damage Description`,
            d.acquisition_cost AS `Acquisition Cost`,
            d.date_acquired AS `Date Acquired`
        FROM devices_full d
        LEFT JOIN departments dept ON dept.department_id = d.department_id
        WHERE d.status = 'Damaged'

        UNION ALL

        SELECT 
            p.pcname AS Name,
            'PC' AS Category,
            dept.department_name AS Department,
            p.location AS Location,
            p.accountable AS Accountable,
            CASE 
                WHEN p.damage_severity IS NULL OR p.damage_severity = '' THEN 'Minor'
                ELSE p.damage_severity
            END AS Severity,
            p.damage_description AS `Damage Description`,
            p.acquisition_cost AS `Acquisition Cost`,
            p.date_acquired AS `Date Acquired`
        FROM pcinfofull p
        LEFT JOIN departments dept ON dept.department_id = p.department_id
        WHERE p.status = 'Damaged'
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
    if severity and severity.lower() != "all":
        filters.append("Severity = %s")
        params.append(severity)
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
        download_name="Damage_Reports.xlsx",
        as_attachment=True
    )


# -------------------------------
# 2️⃣ Get Damage Reports Data
# -------------------------------
@damage_report_bp.route('/get-damage-reports', methods=['GET'])
@check_permission('damage_report', 'view')
def get_damage_reports():
    """
    Get damaged items from devices_full and pcinfofull tables.
    Supports filters like name, category, department, severity, and date range.
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Filters
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    department = request.args.get('department', '').strip()
    severity = request.args.get('severity', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    # Base query combining both tables with damaged items only
    query = """
        SELECT 
            d.accession_id AS id,
            d.item_name AS name,
            d.device_type AS category,
            dept.department_name AS department,
            '' AS location,
            d.accountable,
            d.status,
            CASE 
                WHEN d.damage_severity IS NULL OR d.damage_severity = '' THEN 'Minor'
                ELSE d.damage_severity
            END AS severity,
            d.damage_description,
            d.acquisition_cost,
            d.date_acquired
        FROM devices_full d
        LEFT JOIN departments dept ON dept.department_id = d.department_id
        WHERE d.status = 'Damaged'

        UNION ALL

        SELECT 
            p.pcid AS id,
            p.pcname AS name,
            'PC' AS category,
            dept.department_name AS department,
            p.location,
            p.accountable,
            p.status,
            CASE 
                WHEN p.damage_severity IS NULL OR p.damage_severity = '' THEN 'Minor'
                ELSE p.damage_severity
            END AS severity,
            p.damage_description,
            p.acquisition_cost,
            p.date_acquired
        FROM pcinfofull p
        LEFT JOIN departments dept ON dept.department_id = p.department_id
        WHERE p.status = 'Damaged'
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
    if severity and severity.lower() != "all":
        filters.append("severity = %s")
        params.append(severity)
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

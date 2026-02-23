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


@damage_report_bp.route('/get-damage-reports', methods=['GET'])
@check_permission('damage_report', 'view')
def get_damage_reports():

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Filters
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    department = request.args.get('department', '').strip()
    severity = request.args.get('severity', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    query = """
        SELECT 
            dr.id,
            p.pcname AS name,
            'PC' AS category,
            dept.department_name AS department,
            p.location,
            p.accountable,
            dr.damage_type,
            dr.description AS damage_description,
            p.acquisition_cost,
            p.date_acquired,
            dr.date_reported
        FROM damage_reports dr
        LEFT JOIN pcinfofull p ON dr.pcid = p.pcid
        LEFT JOIN departments dept ON dept.department_id = p.department_id
        WHERE dr.pcid IS NOT NULL
    """

    filters = []
    params = []

    if name:
        filters.append("p.pcname LIKE %s")
        params.append(f"%{name}%")

    if category and category.lower() != "all":
        filters.append("'PC' = %s")
        params.append(category)

    if department and department.lower() != "all":
        filters.append("dept.department_name = %s")
        params.append(department)

    if severity and severity.lower() != "all":
        filters.append("dr.damage_type = %s")  # using damage_type instead
        params.append(severity)

    if date_from:
        filters.append("p.date_acquired >= %s")
        params.append(date_from)

    if date_to:
        filters.append("p.date_acquired <= %s")
        params.append(date_to)

    if filters:
        query += " AND " + " AND ".join(filters)

    query += " ORDER BY dr.date_reported DESC"

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)
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
def loadDamageReports():

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Filters
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    department = request.args.get('department', '').strip()
    status = request.args.get('status', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page

    query = """
        SELECT 
            d.accession_id AS id,
            d.item_name AS name,
            'Device' AS category,
            dept.department_name AS department,
            '' AS location,
            d.accountable,
            d.status,
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
            p.acquisition_cost,
            p.date_acquired
        FROM pcinfofull p
        LEFT JOIN departments dept ON dept.department_id = p.department_id
        WHERE p.status = 'Damaged'
    """

    filters = []
    params = []

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

    # ---------- TOTAL COUNT ----------
    count_query = f"SELECT COUNT(*) as total FROM ({query}) as count_table"
    cursor.execute(count_query, params)
    total = cursor.fetchone()["total"]

    # ---------- PAGINATION ----------
    query += " ORDER BY date_acquired DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total + per_page - 1) // per_page

    return jsonify({
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
    })
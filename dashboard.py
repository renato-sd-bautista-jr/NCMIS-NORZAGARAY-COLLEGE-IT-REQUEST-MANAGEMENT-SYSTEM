from db import get_db_connection
from flask import Blueprint, render_template,session, redirect, url_for, flash
import pymysql

dashboard_bp = Blueprint('dashboard_bp', __name__, template_folder='templates')


@dashboard_bp.route('/dashboardgenerator')
def dashboard_generator_page():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied. Admins only.", "error")
        return redirect(url_for('login_bp.login'))
    return render_template('dashboard.html')
    

@dashboard_bp.route('/dashboardlist')
def dashboard_list():
    
    return render_template('dashboard.html')


@dashboard_bp.route('/dashboardload')
def dashboard_load():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Count all units
            cur.execute("SELECT COUNT(*) AS total FROM devices_units")
            total_items = cur.fetchone()['total']

            # Count Available
            cur.execute("SELECT COUNT(*) AS total FROM devices_units WHERE status = 'Available'")
            available_items = cur.fetchone()['total']            

            # Count Damaged
            cur.execute("SELECT COUNT(*) AS total FROM devices_units WHERE status = 'Damaged'")
            damaged_items = cur.fetchone()['total']

    finally:
        conn.close()

    # Pass counts to the dashboard template
    return render_template(
        'dashboard.html',
        total_items=total_items,
        available_items=available_items,        
        damaged_items=damaged_items
    )
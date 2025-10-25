from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from db import get_db_connection
import pymysql

dashboard_bp = Blueprint('dashboard_bp', __name__, template_folder='templates')


@dashboard_bp.route('/dashboardgenerator')
def dashboard_generator_page():
    """Admin-only access to dashboard generator page."""
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied. Admins only.", "error")
        return redirect(url_for('login_bp.login'))
    return render_template('dashboard.html')


@dashboard_bp.route('/dashboardlist')
def dashboard_list():
    """Fallback route for dashboard."""
    return redirect(url_for('dashboard_bp.dashboard_load'))


@dashboard_bp.route('/dashboardload')
def dashboard_load():
    """Main dashboard data loading route."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:

            # 🔹 Manage Items Count (devices_full)
            cur.execute("SELECT COUNT(*) AS total FROM devices_full")
            total_items = cur.fetchone()['total']

            # 🔹 PC Inventory Count (pcs)
            cur.execute("SELECT COUNT(*) AS total FROM pcs")
            total_pcs = cur.fetchone()['total']

            # 🔹 Status Counts (from devices_units)
            cur.execute("SELECT COUNT(*) AS total FROM devices_units WHERE status = 'Available'")
            available_items = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) AS total FROM devices_units WHERE status = 'Borrowed'")
            in_use_items = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) AS total FROM pcinfofull WHERE status = 'Damaged'")
            damaged_items = cur.fetchone()['total']

            # 🔹 Cost In / Out (not in DB yet — default to 0)
            total_cost_in = 0.00
            total_cost_out = 0.00

            # 🔹 Recent Transactions (optional — only if table exists)
            try:
                cur.execute("""
                    SELECT action, item_name, created_at 
                    FROM transactions 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                recent_transactions = cur.fetchall()
            except Exception:
                recent_transactions = []

    except Exception as e:
        print("❌ Dashboard load error:", e)
        flash("Error loading dashboard data.", "error")
        return render_template(
            'dashboard.html',
            total_items=0,
            total_pcs=0,
            available_items=0,
            in_use_items=0,
            damaged_items=0,
            total_cost_in=0,
            total_cost_out=0,
            recent_transactions=[]
        )
    finally:
        conn.close()

    # ✅ Pass data to dashboard.html
    return render_template(
        'dashboard.html',
        total_items=total_items,          # Manage Items count (devices_full)
        total_pcs=total_pcs,              # PC Inventory count (pcs)
        available_items=available_items,  # Available from devices_units
        in_use_items=in_use_items,        # Borrowed = In Use
        damaged_items=damaged_items,      # Damaged from devices_units
        total_cost_in=total_cost_in,      # Placeholder ₱0.00
        total_cost_out=total_cost_out,    # Placeholder ₱0.00
        recent_transactions=recent_transactions
    )


@dashboard_bp.route('/cost_data/<filter_type>')
def cost_data(filter_type):
    """Mock data for cost chart (replace with SQL aggregation if needed)."""
    data = {}
    if filter_type == 'Weekly':
        data = {
            "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "cost_in": [5000, 8000, 6000, 9000],
            "cost_out": [3000, 4000, 3500, 4500]
        }
    elif filter_type == 'Monthly':
        data = {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "cost_in": [20000, 18000, 15000, 22000, 25000, 30000],
            "cost_out": [12000, 10000, 8000, 15000, 17000, 20000]
        }
    elif filter_type == 'Yearly':
        data = {
            "labels": ["2020", "2021", "2022", "2023", "2024"],
            "cost_in": [150000, 160000, 175000, 180000, 200000],
            "cost_out": [100000, 95000, 110000, 120000, 130000]
        }
    else:
        data = {"labels": [], "cost_in": [], "cost_out": []}

    return jsonify(data)

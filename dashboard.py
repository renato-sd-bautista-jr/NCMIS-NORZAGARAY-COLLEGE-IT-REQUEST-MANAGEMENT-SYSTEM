from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from db import get_db_connection
import pymysql

from datetime import datetime

dashboard_bp = Blueprint('dashboard_bp', __name__, template_folder='templates')




@dashboard_bp.route('/dashboardlist')
def dashboard_list():
    """Fallback route for dashboard."""
    return redirect(url_for('dashboard_bp.dashboard_load'))

@dashboard_bp.route('/cost_data/<string:filter_type>')
def cost_data(filter_type):
    """
    Returns JSON for cost chart.
    Currently only supports monthly totals for the current year.
    """
    conn = get_db_connection()
    try:
        current_year = datetime.now().year

        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Initialize a dictionary with 12 months
            monthly_cost = {m: 0 for m in range(1, 13)}

            # Sum acquisition cost per month from devices_full
            cur.execute("""
                SELECT MONTH(created_at) AS month, SUM(acquisition_cost) AS total
                FROM devices_full
                WHERE YEAR(created_at) = %s
                GROUP BY MONTH(created_at)
            """, (current_year,))
            for row in cur.fetchall():
                monthly_cost[row['month']] += float(row['total'] or 0)

            # Sum acquisition cost per month from pcinfofull
            cur.execute("""
                SELECT MONTH(created_at) AS month, SUM(acquisition_cost) AS total
                FROM pcinfofull
                WHERE YEAR(created_at) = %s
                GROUP BY MONTH(created_at)
            """, (current_year,))
            for row in cur.fetchall():
                monthly_cost[row['month']] += float(row['total'] or 0)

        # Prepare chart data
        labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        cost_in = [monthly_cost[i] for i in range(1,13)]

        return jsonify({
            'labels': labels,
            'cost_in': cost_in
        })

    except Exception as e:
        print("❌ Cost chart error:", e)
        return jsonify({'labels': [], 'cost_in': []})
    finally:
        conn.close()

        
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
            cur.execute("SELECT COUNT(*) AS total FROM pcinfofull")
            total_pcs = cur.fetchone()['total']

            # 🔹 Status Counts (from devices_units)
            cur.execute("SELECT COUNT(*) AS total FROM devices_full WHERE status = 'Available'")
            available_devices = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) AS total FROM pcinfofull WHERE status = 'Available'")
            available_pc = cur.fetchone()['total']

            available_items = available_devices + available_pc

            cur.execute("SELECT COUNT(*) AS total FROM devices_full WHERE status = 'In Used'")
            
            in_use_items = cur.fetchone()['total']

            
            cur.execute("SELECT COUNT(*) AS total FROM devices_full WHERE status = 'Damaged'")
            damaged_pc = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) AS total FROM pcinfofull WHERE status = 'Damaged'")
            damaged_devices = cur.fetchone()['total']
            damaged_items= damaged_pc + damaged_devices

                # 🔹 Total Cost In (sum of acquisition_cost from both tables)
            cur.execute("SELECT IFNULL(SUM(acquisition_cost), 0) AS total FROM devices_full")
            device_cost = cur.fetchone()['total']

            cur.execute("SELECT IFNULL(SUM(acquisition_cost), 0) AS total FROM pcinfofull")
            pc_cost = cur.fetchone()['total']

            # Average cost
            cur.execute("""
                SELECT AVG(acquisition_cost) AS avg_cost FROM (
                    SELECT acquisition_cost FROM devices_full
                    UNION ALL
                    SELECT acquisition_cost FROM pcinfofull
                ) AS combined
            """)
            avg_cost = cur.fetchone()['avg_cost'] or 0

            total_cost_in = float(device_cost) + float(pc_cost)

            cur.execute("""
                SELECT item_name AS item_name, brand_model AS action, created_at 
                FROM devices_full 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_transactions = cur.fetchall()

            
            

    except Exception as e:
        print("❌ Dashboard load error:", e)
        flash("Error loading dashboard data.", "error")
        return render_template('dashboard.html',
            total_items=0,
            total_pcs=0,
            available_items=0,
            in_use_items=0,
            damaged_items=0,
            total_cost_in=0,
            avg_cost=avg_cost,
            recent_transactions=recent_transactions
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
        recent_transactions=recent_transactions
    )



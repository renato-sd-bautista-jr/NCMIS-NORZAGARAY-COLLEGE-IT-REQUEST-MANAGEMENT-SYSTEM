from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from db import get_db_connection
import pymysql

from datetime import datetime

dashboard_bp = Blueprint('dashboard_bp', __name__, template_folder='templates')




@dashboard_bp.route('/dashboardlist')
def dashboard_list():
    """Fallback route for dashboard."""
    return redirect(url_for('dashboard_bp.dashboard_load'))

@dashboard_bp.route('/inventory_category_data')
def inventory_category_data():
    """Returns JSON for inventory by category chart."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Get device categories from devices_full
            cur.execute("""
                SELECT device_type as category, COUNT(*) as count, SUM(acquisition_cost) as total_cost
                FROM devices_full
                WHERE device_type IS NOT NULL AND device_type != ''
                GROUP BY device_type
                ORDER BY count DESC
            """)
            device_categories = cur.fetchall()
            
            # Get PCs as a separate category
            cur.execute("""
                SELECT 'PCs' as category, COUNT(*) as count, SUM(acquisition_cost) as total_cost
                FROM pcinfofull
            """)
            pc_data = cur.fetchone()
            
            # Combine data
            categories = device_categories
            if pc_data and pc_data['count'] > 0:
                categories.append(pc_data)
            
            return jsonify({
                'categories': [cat['category'] for cat in categories],
                'counts': [cat['count'] for cat in categories],
                'costs': [float(cat['total_cost'] or 0) for cat in categories]
            })
            
    except Exception as e:
        print("❌ Inventory category data error:", e)
        return jsonify({'categories': [], 'counts': [], 'costs': []})
    finally:
        conn.close()

@dashboard_bp.route('/stock_status_data')
def stock_status_data():
    """Returns JSON for stock status distribution chart."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Get device statuses
            cur.execute("""
                SELECT status, COUNT(*) as count
                FROM devices_full
                GROUP BY status
            """)
            device_statuses = cur.fetchall()
            
            # Get PC statuses
            cur.execute("""
                SELECT status, COUNT(*) as count
                FROM pcinfofull
                GROUP BY status
            """)
            pc_statuses = cur.fetchall()
            
            # Combine and aggregate statuses
            status_map = {}
            
            # Add device counts
            for status in device_statuses:
                status_name = status['status'] or 'Unknown'
                status_map[status_name] = status_map.get(status_name, 0) + status['count']
            
            # Add PC counts
            for status in pc_statuses:
                status_name = status['status'] or 'Unknown'
                status_map[status_name] = status_map.get(status_name, 0) + status['count']
            
            return jsonify({
                'statuses': list(status_map.keys()),
                'counts': list(status_map.values())
            })
            
    except Exception as e:
        print("❌ Stock status data error:", e)
        return jsonify({'statuses': [], 'counts': []})
    finally:
        conn.close()

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

        
@dashboard_bp.route('/consumable_analytics_data')
def consumable_analytics_data():
    """Returns JSON for consumable analytics."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Get consumable usage rate statistics
            cur.execute("""
                SELECT 
                    c.consumable_name,
                    c.quantity as current_quantity,
                    c.minimum_level,
                    c.maximum_level,
                    c.unit_cost,
                    c.last_restocked,
                    COALESCE(SUM(cl.quantity_used), 0) as total_used,
                    COUNT(cl.consumable_log_id) as usage_count,
                    AVG(cl.quantity_used) as avg_usage_per_transaction,
                    MAX(cl.usage_date) as last_usage_date,
                    DATEDIFF(CURDATE(), c.last_restocked) as days_since_restock,
                    CASE 
                        WHEN c.quantity <= c.minimum_level THEN 'Critical'
                        WHEN c.quantity <= (c.minimum_level * 1.5) THEN 'Low'
                        WHEN c.quantity >= c.maximum_level THEN 'Overstocked'
                        ELSE 'Normal'
                    END as stock_status
                FROM consumables c
                LEFT JOIN consumable_logs cl ON c.consumable_id = cl.consumable_id
                GROUP BY c.consumable_id, c.consumable_name, c.quantity, c.minimum_level, c.maximum_level, c.unit_cost, c.last_restocked
                ORDER BY total_used DESC
            """)
            consumable_usage = cur.fetchall()
            
            # Get reorder analytics
            cur.execute("""
                SELECT 
                    c.consumable_name,
                    c.quantity as current_quantity,
                    c.minimum_level,
                    c.maximum_level,
                    c.unit_cost,
                    c.last_restocked,
                    COALESCE(SUM(cl.quantity_used), 0) as total_used,
                    CASE 
                        WHEN c.quantity <= c.minimum_level THEN 'Immediate'
                        WHEN c.quantity <= (c.minimum_level + (c.minimum_level * 0.2)) THEN 'Soon'
                        WHEN DATEDIFF(CURDATE(), c.last_restocked) > 30 THEN 'Review'
                        ELSE 'Monitor'
                    END as reorder_priority,
                    ROUND(c.quantity / NULLIF(AVG(cl.quantity_used), 0), 0) as estimated_days_remaining,
                    ROUND((c.minimum_level - c.quantity) / NULLIF(AVG(cl.quantity_used), 0), 0) as days_until_reorder,
                    (c.minimum_level - c.quantity) as quantity_needed
                FROM consumables c
                LEFT JOIN consumable_logs cl ON c.consumable_id = cl.consumable_id
                WHERE cl.usage_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY c.consumable_id, c.consumable_name, c.quantity, c.minimum_level, c.maximum_level, c.unit_cost, c.last_restocked
                ORDER BY 
                    CASE 
                        WHEN c.quantity <= c.minimum_level THEN 1
                        WHEN c.quantity <= (c.minimum_level + (c.minimum_level * 0.2)) THEN 2
                        ELSE 3
                    END,
                    days_until_reorder ASC
            """)
            reorder_analytics = cur.fetchall()
            
            # Get cost analysis over time
            cur.execute("""
                SELECT 
                    DATE_FORMAT(cl.usage_date, '%Y-%m') as month,
                    SUM(cl.quantity_used * c.unit_cost) as monthly_cost,
                    SUM(cl.quantity_used) as monthly_quantity,
                    COUNT(DISTINCT c.consumable_id) as active_consumables
                FROM consumable_logs cl
                JOIN consumables c ON cl.consumable_id = c.consumable_id
                WHERE cl.usage_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                GROUP BY DATE_FORMAT(cl.usage_date, '%Y-%m')
                ORDER BY month DESC
            """)
            cost_over_time = cur.fetchall()
            
            # Get consumable type analysis
            cur.execute("""
                SELECT 
                    c.consumable_name,
                    c.quantity as current_quantity,
                    c.minimum_level,
                    c.unit_cost,
                    COALESCE(SUM(cl.quantity_used), 0) as total_used,
                    (c.quantity * c.unit_cost) as current_value,
                    ROUND(AVG(cl.quantity_used), 2) as avg_monthly_usage,
                    ROUND(DATEDIFF(CURDATE(), c.last_restocked) * AVG(cl.quantity_used) / 30, 2) as projected_usage,
                    CASE 
                        WHEN AVG(cl.quantity_used) > 0 THEN 
                            ROUND(c.quantity / AVG(cl.quantity_used), 0)
                        ELSE 999 
                    END as days_of_supply
                FROM consumables c
                LEFT JOIN consumable_logs cl ON c.consumable_id = cl.consumable_id
                WHERE cl.usage_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY) OR cl.usage_date IS NULL
                GROUP BY c.consumable_id, c.consumable_name, c.quantity, c.minimum_level, c.unit_cost, c.last_restocked
                ORDER BY current_value DESC
            """)
            consumable_analysis = cur.fetchall()
            
            # Get top consumable users
            cur.execute("""
                SELECT 
                    d.department_name,
                    COUNT(cl.consumable_log_id) as usage_count,
                    SUM(cl.quantity_used) as total_quantity,
                    SUM(cl.quantity_used * c.unit_cost) as total_cost,
                    AVG(cl.quantity_used) as avg_per_usage
                FROM consumable_logs cl
                JOIN consumables c ON cl.consumable_id = c.consumable_id
                LEFT JOIN departments d ON cl.department_id = d.department_id
                WHERE cl.usage_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY d.department_name
                ORDER BY total_cost DESC
                LIMIT 10
            """)
            top_users = cur.fetchall()
            
            return jsonify({
                'consumable_usage': consumable_usage,
                'reorder_analytics': reorder_analytics,
                'cost_over_time': cost_over_time,
                'consumable_analysis': consumable_analysis,
                'top_users': top_users
            })
            
    except Exception as e:
        print("❌ Consumable analytics data error:", e)
        return jsonify({
            'consumable_usage': [],
            'reorder_analytics': [],
            'cost_over_time': [],
            'consumable_analysis': [],
            'top_users': []
        })
    finally:
        conn.close()

@dashboard_bp.route('/maintenance_analytics_data')
def maintenance_analytics_data():
    """Returns JSON for maintenance analytics."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Get maintenance frequency statistics
            cur.execute("""
                SELECT 
                    'Device' as asset_type,
                    COUNT(*) as total_assets,
                    COUNT(CASE WHEN last_checked IS NOT NULL THEN 1 END) as assets_with_maintenance,
                    COUNT(CASE WHEN last_checked IS NOT NULL AND 
                              DATEDIFF(CURDATE(), last_checked) >= maintenance_interval_days THEN 1 END) as overdue_maintenance,
                    AVG(maintenance_interval_days) as avg_maintenance_interval,
                    AVG(DATEDIFF(CURDATE(), COALESCE(last_checked, created_at))) as avg_days_since_last_check
                FROM devices_full
                WHERE maintenance_interval_days IS NOT NULL
                
                UNION ALL
                
                SELECT 
                    'PC' as asset_type,
                    COUNT(*) as total_assets,
                    COUNT(CASE WHEN last_checked IS NOT NULL THEN 1 END) as assets_with_maintenance,
                    COUNT(CASE WHEN last_checked IS NOT NULL AND 
                              DATEDIFF(CURDATE(), last_checked) >= maintenance_interval_days THEN 1 END) as overdue_maintenance,
                    AVG(maintenance_interval_days) as avg_maintenance_interval,
                    AVG(DATEDIFF(CURDATE(), COALESCE(last_checked, created_at))) as avg_days_since_last_check
                FROM pcinfofull
                WHERE maintenance_interval_days IS NOT NULL
            """)
            maintenance_frequency = cur.fetchall()
            
            # Get maintenance costs by asset type
            cur.execute("""
                SELECT 
                    'Device' as asset_type,
                    COUNT(*) as total_maintenance_records,
                    AVG(DATEDIFF(last_checked, COALESCE(
                        (SELECT MAX(performed_at) 
                         FROM asset_maintenance_logs aml 
                         WHERE aml.asset_type = 'Device' AND aml.asset_id = df.accession_id 
                         AND aml.performed_at < df.last_checked
                         ORDER BY performed_at DESC LIMIT 1), 
                        df.created_at
                    ))) as avg_days_between_maintenance,
                    COUNT(CASE WHEN status = 'Damaged' THEN 1 END) as damaged_count,
                    ROUND(COUNT(CASE WHEN status = 'Damaged' THEN 1 END) * 100.0 / COUNT(*), 2) as damage_rate
                FROM devices_full df
                WHERE last_checked IS NOT NULL
                GROUP BY 'Device'
                
                UNION ALL
                
                SELECT 
                    'PC' as asset_type,
                    COUNT(*) as total_maintenance_records,
                    AVG(DATEDIFF(last_checked, COALESCE(
                        (SELECT MAX(performed_at) 
                         FROM asset_maintenance_logs aml 
                         WHERE aml.asset_type = 'PC' AND aml.asset_id = pcf.pcid 
                         AND aml.performed_at < pcf.last_checked
                         ORDER BY performed_at DESC LIMIT 1), 
                        pcf.created_at
                    ))) as avg_days_between_maintenance,
                    COUNT(CASE WHEN status = 'Damaged' THEN 1 END) as damaged_count,
                    ROUND(COUNT(CASE WHEN status = 'Damaged' THEN 1 END) * 100.0 / COUNT(*), 2) as damage_rate
                FROM pcinfofull pcf
                WHERE last_checked IS NOT NULL
                GROUP BY 'PC'
            """)
            maintenance_costs = cur.fetchall()
            
            # Get device type specific maintenance data
            cur.execute("""
                SELECT 
                    device_type,
                    COUNT(*) as total_assets,
                    COUNT(CASE WHEN last_checked IS NOT NULL THEN 1 END) as maintained_assets,
                    AVG(maintenance_interval_days) as avg_interval,
                    COUNT(CASE WHEN status = 'Damaged' THEN 1 END) as damaged_assets,
                    ROUND(COUNT(CASE WHEN status = 'Damaged' THEN 1 END) * 100.0 / COUNT(*), 2) as damage_rate,
                    SUM(acquisition_cost) as total_value,
                    ROUND(SUM(acquisition_cost) * COUNT(CASE WHEN status = 'Damaged' THEN 1 END) / COUNT(*), 2) as estimated_repair_cost
                FROM devices_full
                WHERE device_type IS NOT NULL AND device_type != ''
                GROUP BY device_type
                ORDER BY damaged_assets DESC
            """)
            device_type_maintenance = cur.fetchall()
            
            # Get maintenance logs for trend analysis
            cur.execute("""
                SELECT 
                    asset_type,
                    DATE(performed_at) as maintenance_date,
                    COUNT(*) as maintenance_count
                FROM asset_maintenance_logs
                WHERE performed_at >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                GROUP BY asset_type, DATE(performed_at)
                ORDER BY maintenance_date DESC
            """)
            maintenance_trends = cur.fetchall()
            
            # Get upcoming maintenance schedule
            cur.execute("""
                SELECT 
                    'Device' as asset_type,
                    accession_id as asset_id,
                    item_name,
                    brand_model,
                    device_type,
                    last_checked,
                    maintenance_interval_days,
                    DATEDIFF(DATE_ADD(last_checked, INTERVAL maintenance_interval_days DAY), CURDATE()) as days_until_maintenance,
                    CASE 
                        WHEN DATEDIFF(DATE_ADD(last_checked, INTERVAL maintenance_interval_days DAY), CURDATE()) <= 0 THEN 'Overdue'
                        WHEN DATEDIFF(DATE_ADD(last_checked, INTERVAL maintenance_interval_days DAY), CURDATE()) <= 7 THEN 'Due Soon'
                        ELSE 'Scheduled'
                    END as maintenance_status
                FROM devices_full
                WHERE last_checked IS NOT NULL AND maintenance_interval_days IS NOT NULL
                ORDER BY days_until_maintenance ASC
                LIMIT 10
                
                UNION ALL
                
                SELECT 
                    'PC' as asset_type,
                    pcid as asset_id,
                    pcname as item_name,
                    '' as brand_model,
                    'PC' as device_type,
                    last_checked,
                    maintenance_interval_days,
                    DATEDIFF(DATE_ADD(last_checked, INTERVAL maintenance_interval_days DAY), CURDATE()) as days_until_maintenance,
                    CASE 
                        WHEN DATEDIFF(DATE_ADD(last_checked, INTERVAL maintenance_interval_days DAY), CURDATE()) <= 0 THEN 'Overdue'
                        WHEN DATEDIFF(DATE_ADD(last_checked, INTERVAL maintenance_interval_days DAY), CURDATE()) <= 7 THEN 'Due Soon'
                        ELSE 'Scheduled'
                    END as maintenance_status
                FROM pcinfofull
                WHERE last_checked IS NOT NULL AND maintenance_interval_days IS NOT NULL
                ORDER BY days_until_maintenance ASC
                LIMIT 10
            """)
            upcoming_maintenance = cur.fetchall()
            
            return jsonify({
                'maintenance_frequency': maintenance_frequency,
                'maintenance_costs': maintenance_costs,
                'device_type_maintenance': device_type_maintenance,
                'maintenance_trends': maintenance_trends,
                'upcoming_maintenance': upcoming_maintenance
            })
            
    except Exception as e:
        print("❌ Maintenance analytics data error:", e)
        return jsonify({
            'maintenance_frequency': [],
            'maintenance_costs': [],
            'device_type_maintenance': [],
            'maintenance_trends': [],
            'upcoming_maintenance': []
        })
    finally:
        conn.close()

@dashboard_bp.route('/department_analytics_data')
def department_analytics_data():
    """Returns JSON for department analytics."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Get department usage statistics
            cur.execute("""
                SELECT 
                    d.department_name,
                    COUNT(DISTINCT df.accession_id) as device_count,
                    COUNT(DISTINCT pcf.pcid) as pc_count,
                    (COUNT(DISTINCT df.accession_id) + COUNT(DISTINCT pcf.pcid)) as total_assets,
                    COALESCE(SUM(df.acquisition_cost), 0) + COALESCE(SUM(pcf.acquisition_cost), 0) as total_cost,
                    COUNT(DISTINCT CASE WHEN df.status = 'In Used' THEN df.accession_id END) +
                    COUNT(DISTINCT CASE WHEN pcf.status = 'In Used' THEN pcf.pcid END) as in_use_count,
                    COUNT(DISTINCT CASE WHEN df.status = 'Available' THEN df.accession_id END) +
                    COUNT(DISTINCT CASE WHEN pcf.status = 'Available' THEN pcf.pcid END) as available_count
                FROM departments d
                LEFT JOIN devices_full df ON d.department_id = df.department_id
                LEFT JOIN pcinfofull pcf ON d.department_id = pcf.department_id
                GROUP BY d.department_id, d.department_name
                ORDER BY total_assets DESC
            """)
            department_usage = cur.fetchall()
            
            # Get cross-department efficiency metrics
            cur.execute("""
                SELECT 
                    d.department_name,
                    COUNT(DISTINCT br.borrow_id) as total_borrows,
                    COUNT(DISTINCT CASE WHEN br.status = 'Returned' THEN br.borrow_id END) as returned_borrows,
                    AVG(DATEDIFF(COALESCE(br.return_date, CURDATE()), br.borrow_date)) as avg_borrow_days,
                    ROUND(COUNT(DISTINCT CASE WHEN br.status = 'Returned' THEN br.borrow_id END) * 100.0 / 
                          COUNT(DISTINCT br.borrow_id), 2) as return_rate,
                    (COUNT(DISTINCT df.accession_id) + COUNT(DISTINCT pcf.pcid)) as total_assets,
                    ROUND(COUNT(DISTINCT br.borrow_id) * 1.0 / 
                          NULLIF((COUNT(DISTINCT df.accession_id) + COUNT(DISTINCT pcf.pcid)), 0), 2) as utilization_rate
                FROM departments d
                LEFT JOIN devices_full df ON d.department_id = df.department_id
                LEFT JOIN pcinfofull pcf ON d.department_id = pcf.department_id
                LEFT JOIN borrow_requests br ON (df.accession_id = br.device_id OR pcf.pcid = br.device_id)
                GROUP BY d.department_id, d.department_name
                HAVING total_assets > 0
                ORDER BY utilization_rate DESC
            """)
            department_efficiency = cur.fetchall()
            
            # Get cost per department breakdown
            cur.execute("""
                SELECT 
                    d.department_name,
                    COALESCE(SUM(df.acquisition_cost), 0) as device_costs,
                    COALESCE(SUM(pcf.acquisition_cost), 0) as pc_costs,
                    COALESCE(SUM(df.acquisition_cost), 0) + COALESCE(SUM(pcf.acquisition_cost), 0) as total_costs,
                    COUNT(DISTINCT df.accession_id) + COUNT(DISTINCT pcf.pcid) as asset_count,
                    ROUND((COALESCE(SUM(df.acquisition_cost), 0) + COALESCE(SUM(pcf.acquisition_cost), 0)) / 
                          NULLIF(COUNT(DISTINCT df.accession_id) + COUNT(DISTINCT pcf.pcid), 0), 2) as avg_cost_per_asset
                FROM departments d
                LEFT JOIN devices_full df ON d.department_id = df.department_id
                LEFT JOIN pcinfofull pcf ON d.department_id = pcf.department_id
                GROUP BY d.department_id, d.department_name
                ORDER BY total_costs DESC
            """)
            department_costs = cur.fetchall()
            
            # Get monthly department usage trends
            current_year = datetime.now().year
            cur.execute("""
                SELECT 
                    d.department_name,
                    MONTH(br.borrow_date) as month,
                    COUNT(*) as borrow_count
                FROM departments d
                LEFT JOIN devices_full df ON d.department_id = df.department_id
                LEFT JOIN pcinfofull pcf ON d.department_id = pcf.department_id
                LEFT JOIN borrow_requests br ON (df.accession_id = br.device_id OR pcf.pcid = br.device_id)
                WHERE YEAR(br.borrow_date) = %s AND br.borrow_date IS NOT NULL
                GROUP BY d.department_id, d.department_name, MONTH(br.borrow_date)
                ORDER BY month, department_name
            """, (current_year,))
            monthly_trends = cur.fetchall()
            
            return jsonify({
                'department_usage': department_usage,
                'department_efficiency': department_efficiency,
                'department_costs': department_costs,
                'monthly_trends': monthly_trends
            })
            
    except Exception as e:
        print("❌ Department analytics data error:", e)
        return jsonify({
            'department_usage': [],
            'department_efficiency': [],
            'department_costs': [],
            'monthly_trends': []
        })
    finally:
        conn.close()

@dashboard_bp.route('/return_rate_data')
def return_rate_data():
    """Returns JSON for return rate analysis."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Get return rate statistics
            cur.execute("""
                SELECT 
                    COUNT(*) as total_borrowed,
                    SUM(CASE WHEN status = 'Returned' THEN 1 ELSE 0 END) as returned_count,
                    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_count,
                    SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved_count,
                    AVG(DATEDIFF(COALESCE(return_date, CURDATE()), borrow_date)) as avg_days_borrowed
                FROM borrow_requests
                WHERE borrow_date IS NOT NULL
            """)
            stats = cur.fetchone()
            
            # Get monthly return trends for the current year
            current_year = datetime.now().year
            cur.execute("""
                SELECT 
                    MONTH(borrow_date) as month,
                    COUNT(*) as borrowed,
                    SUM(CASE WHEN status = 'Returned' THEN 1 ELSE 0 END) as returned
                FROM borrow_requests
                WHERE YEAR(borrow_date) = %s
                GROUP BY MONTH(borrow_date)
                ORDER BY month
            """, (current_year,))
            monthly_trends = cur.fetchall()
            
            # Get return rate by device type
            cur.execute("""
                SELECT 
                    df.device_type,
                    COUNT(*) as total_borrowed,
                    SUM(CASE WHEN br.status = 'Returned' THEN 1 ELSE 0 END) as returned_count,
                    ROUND(SUM(CASE WHEN br.status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as return_rate
                FROM borrow_requests br
                LEFT JOIN devices_full df ON br.device_id = df.accession_id
                WHERE br.borrow_date IS NOT NULL
                GROUP BY df.device_type
                ORDER BY return_rate DESC
            """)
            device_type_stats = cur.fetchall()
            
            # Get overdue returns
            cur.execute("""
                SELECT 
                    br.borrow_id,
                    br.student_id,
                    br.last_name,
                    br.first_name,
                    df.item_name,
                    df.brand_model,
                    br.borrow_date,
                    br.return_date,
                    DATEDIFF(CURDATE(), br.borrow_date) as days_overdue
                FROM borrow_requests br
                LEFT JOIN devices_full df ON br.device_id = df.accession_id
                WHERE br.status IN ('Pending', 'Approved') 
                AND br.borrow_date < DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                ORDER BY days_overdue DESC
                LIMIT 10
            """)
            overdue_returns = cur.fetchall()
            
            return jsonify({
                'stats': {
                    'total_borrowed': stats['total_borrowed'] or 0,
                    'returned_count': stats['returned_count'] or 0,
                    'pending_count': stats['pending_count'] or 0,
                    'approved_count': stats['approved_count'] or 0,
                    'avg_days_borrowed': round(float(stats['avg_days_borrowed'] or 0), 1),
                    'return_rate_percentage': round((stats['returned_count'] or 0) * 100.0 / (stats['total_borrowed'] or 1), 2)
                },
                'monthly_trends': monthly_trends,
                'device_type_stats': device_type_stats,
                'overdue_returns': overdue_returns
            })
            
    except Exception as e:
        print("❌ Return rate data error:", e)
        return jsonify({
            'stats': {'total_borrowed': 0, 'returned_count': 0, 'pending_count': 0, 'approved_count': 0, 'avg_days_borrowed': 0, 'return_rate_percentage': 0},
            'monthly_trends': [],
            'device_type_stats': [],
            'overdue_returns': []
        })
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

            # 🔹 Maintenance Notifications
            cur.execute("""
                SELECT 
                    accession_id,
                    item_name,
                    brand_model,
                    department_name,
                    DATEDIFF(CURDATE(), COALESCE(last_checked, DATE_SUB(CURDATE(), INTERVAL maintenance_interval_days DAY))) as days_since_check,
                    maintenance_interval_days,
                    CASE 
                        WHEN last_checked IS NULL THEN 'Never Checked'
                        WHEN DATEDIFF(CURDATE(), last_checked) >= maintenance_interval_days THEN 'Overdue'
                        WHEN DATEDIFF(CURDATE(), last_checked) >= (maintenance_interval_days * 0.8) THEN 'Due Soon'
                        ELSE 'OK'
                    END as maintenance_status
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                WHERE df.status != 'Damaged'
                ORDER BY days_since_check DESC
                LIMIT 10
            """)
            maintenance_notifications = cur.fetchall()

            cur.execute("""
                SELECT item_name AS item_name, brand_model AS action, created_at 
                FROM devices_full 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_transactions = cur.fetchall()

            # 🔹 Low Stock Alerts (items with quantity <= 2 or status indicating low availability)
            cur.execute("""
                SELECT 'device' as item_type, accession_id as item_id, item_name, brand_model, 
                       quantity, status, device_type, department_name
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                WHERE (quantity <= 2 OR status IN ('Needs Checking', 'Damaged')) AND status != 'Surrendered'
                ORDER BY quantity ASC, status DESC
                LIMIT 10
            """)
            low_stock_devices = cur.fetchall()

            cur.execute("""
                SELECT 'pc' as item_type, pcid as item_id, pcname as item_name, 
                       '' as brand_model, quantity, status, 'PC' as device_type, department_name
                FROM pcinfofull pcf
                LEFT JOIN departments dep ON pcf.department_id = dep.department_id
                WHERE (quantity <= 2 OR status IN ('Needs Checking', 'Damaged')) AND status != 'Surrendered'
                ORDER BY quantity ASC, status DESC
                LIMIT 10
            """)
            low_stock_pcs = cur.fetchall()

            # Combine low stock alerts
            low_stock_alerts = low_stock_devices + low_stock_pcs

            

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
            avg_cost=0,
            recent_transactions=[],
            maintenance_notifications=[],
            low_stock_alerts=[]
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
        recent_transactions=recent_transactions,
        maintenance_notifications=maintenance_notifications,
        low_stock_alerts=low_stock_alerts
    )

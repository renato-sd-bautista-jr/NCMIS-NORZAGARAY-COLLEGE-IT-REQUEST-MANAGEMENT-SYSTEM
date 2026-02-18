from flask import Blueprint, render_template, flash, jsonify, request, redirect, url_for
from db import get_db_connection
import pymysql
import time, random

manage_consumable_bp = Blueprint('manage_consumable_bp', __name__, template_folder='templates')

# ✅ Get Departments
@manage_consumable_bp.route('/get-departments')
def get_departments():
    conn = get_db_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
        results = cur.fetchall()
    conn.close()
    return jsonify(results)

# ✅ Filter Consumables
@manage_consumable_bp.route('/filter-consumable', methods=['GET'])
def filter_consumables():
    """Filter consumables dynamically based on query parameters."""
    conn = get_db_connection()
    try:
        # Get all possible query parameters
        department_id = request.args.get('department_id')
        status = request.args.get('status')
        accountable = request.args.get('accountable')
        item_name = request.args.get('item_name')
        brand_model = request.args.get('brand_model')
        quantity = request.args.get('quantity')
        acquisition_cost = request.args.get('acquisition_cost')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        query = """
            SELECT 
                df.accession_id,
                df.item_name,
                df.brand_model,
                df.quantity,
                df.acquisition_cost,
                df.date_acquired,
                df.accountable,
                df.status,
                df.risk_level,
                df.health_score,
                df.last_checked,
                df.maintenance_interval_days,
                dep.department_id,
                dep.department_name
            FROM devices_full df
            LEFT JOIN departments dep ON df.department_id = dep.department_id
            WHERE df.device_type = 'Consumable'
        """
        params = []

        # Apply filters dynamically
        if department_id:
            query += " AND df.department_id = %s"
            params.append(department_id)
        if status:
            query += " AND df.status = %s"
            params.append(status)
        if accountable:
            query += " AND df.accountable LIKE %s"
            params.append(f"%{accountable}%")
        if item_name:
            query += " AND df.item_name LIKE %s"
            params.append(f"%{item_name}%")
        if brand_model:
            query += " AND df.brand_model LIKE %s"
            params.append(f"%{brand_model}%")
        if quantity:
            query += " AND df.quantity = %s"
            params.append(quantity)
        if acquisition_cost:
            query += " AND df.acquisition_cost = %s"
            params.append(acquisition_cost)

        if date_from and date_to:
            query += " AND df.date_acquired BETWEEN %s AND %s"
            params.extend([date_from, date_to])

        query += " ORDER BY df.accession_id DESC"

        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(query, params)
            consumables = cur.fetchall()

        return jsonify(consumables)

    except Exception as e:
        print(f"❌ Error filtering consumables: {e}")
        return jsonify({"error": "Error filtering consumables."}), 500
    finally:
        conn.close()

# ✅ Get Consumables with Departments
@manage_consumable_bp.route('/get-consumables')
def get_consumables():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    df.accession_id,
                    df.item_name,
                    df.brand_model,
                    df.quantity,
                    df.acquisition_cost,
                    df.date_acquired,
                    df.accountable,
                    df.status,
                    df.risk_level,
                    df.health_score,
                    df.last_checked,
                    df.maintenance_interval_days,
                    dep.department_id,
                    dep.department_name
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                WHERE df.device_type = 'Consumable'
                ORDER BY df.accession_id DESC
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching consumables: {e}")
        return []
    finally:
        conn.close()

@manage_consumable_bp.route('/manage_consumable')
def manage_consumable_page():
    """Load Manage Consumables page."""
    conn = get_db_connection()
    try:
        # Get filter parameters
        department = request.args.get('department')
        status = request.args.get('status')
        
        # Build query with filters
        query = """
            SELECT 
                df.accession_id,
                df.item_name,
                df.brand_model,
                df.quantity,
                df.acquisition_cost,
                df.date_acquired,
                df.accountable,
                df.status,
                df.risk_level,
                df.health_score,
                df.last_checked,
                df.maintenance_interval_days,
                dep.department_id,
                dep.department_name
            FROM devices_full df
            LEFT JOIN departments dep ON df.department_id = dep.department_id
            WHERE df.device_type = 'Consumable'
        """
        params = []
        
        if department:
            query += " AND dep.department_name = %s"
            params.append(department)
        
        if status:
            query += " AND df.status = %s"
            params.append(status)
            
        query += " ORDER BY df.accession_id DESC"

        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(query, params)
            consumables = cur.fetchall()
            
        # Get departments for filter dropdown
        cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
        departments = cur.fetchall()
            
    except Exception as e:
        print(f"Error loading consumables: {e}")
        consumables = []
        departments = []
    finally:
        conn.close()

    return render_template('manage_consumable.html', consumables=consumables, departments=departments)

@manage_consumable_bp.route('/add-consumable', methods=['POST'])
def add_consumable():
    conn = get_db_connection()
    try:
        form = request.form
        item_name = form.get('item_name')
        brand_model = form.get('brand_model')
        acquisition_cost = form.get('acquisition_cost')
        date_acquired = form.get('date_acquired')
        accountable = form.get('accountable')
        department_id = form.get('department_id')
        status = form.get('status') or 'Available'
        quantity = int(form.get('quantity', 1))
        maintenance_interval_days = int(form.get('maintenance_interval_days', 30))

        with conn.cursor() as cur:
            # Auto-generate serials for consumables (internal only)
            serial_no = f"CONS-{int(time.time()*1000) % 1000000}{random.randint(10,99)}"
            municipal_serial_no = f"MC-{int(time.time()*1000) % 1000000}{random.randint(10,99)}"

            cur.execute("""
                INSERT INTO devices_full (
                    item_name, brand_model, serial_no, municipal_serial_no, quantity,
                    device_type, acquisition_cost, date_acquired, accountable,
                    department_id, status, maintenance_interval_days
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                item_name, brand_model, serial_no, municipal_serial_no, quantity,
                'Consumable', acquisition_cost, date_acquired, accountable,
                department_id, status, maintenance_interval_days
            ))

        conn.commit()
        flash("Consumable added successfully!", "success")
        return redirect(url_for('manage_consumable_bp.manage_consumable_page'))
    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding consumable: {e}")
        flash("Error adding consumable.", "danger")
        return redirect(url_for('manage_consumable_bp.manage_consumable_page'))
    finally:
        conn.close()

@manage_consumable_bp.route('/update-consumable', methods=['POST'])
def update_consumable():
    conn = get_db_connection()
    try:
        form = request.form
        accession_id = form.get('accession_id')
        if not accession_id:
            flash("Missing consumable ID.", "danger")
            return redirect(url_for('manage_consumable_bp.manage_consumable_page'))

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE devices_full
                SET item_name=%s,
                    brand_model=%s,
                    quantity=%s,
                    acquisition_cost=%s,
                    date_acquired=%s,
                    accountable=%s,
                    department_id=%s,
                    status=%s,
                    maintenance_interval_days=%s
                WHERE accession_id=%s AND device_type='Consumable'
            """, (
                form.get('item_name'),
                form.get('brand_model'),
                form.get('quantity'),
                form.get('acquisition_cost'),
                form.get('date_acquired'),
                form.get('accountable'),
                form.get('department_id'),
                form.get('status'),
                form.get('maintenance_interval_days', 30),
                accession_id
            ))
            conn.commit()
        flash("Consumable updated successfully!", "success")
        return redirect(url_for('manage_consumable_bp.manage_consumable_page'))
    except Exception as e:
        conn.rollback()
        print(f"❌ Error updating consumable: {e}")
        flash("Error updating consumable.", "danger")
        return redirect(url_for('manage_consumable_bp.manage_consumable_page'))
    finally:
        conn.close()

@manage_consumable_bp.route('/delete-consumable/<int:id>', methods=['POST'])
def delete_consumable(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM devices_full WHERE accession_id = %s AND device_type='Consumable'", (id,))
            conn.commit()
        flash("Consumable deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting consumable: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('manage_consumable_bp.manage_consumable_page'))

@manage_consumable_bp.route('/get-consumable-by-id/<int:item_id>')
def get_consumable_by_id(item_id):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    df.accession_id,
                    df.item_name,
                    df.brand_model,
                    df.quantity,
                    df.acquisition_cost,
                    df.date_acquired,
                    df.accountable,
                    df.status,
                    df.maintenance_interval_days,
                    dep.department_id,
                    dep.department_name
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                WHERE df.accession_id = %s AND df.device_type='Consumable'
            """, (item_id,))
            item = cur.fetchone()

        if not item:
            return jsonify({'error': 'Consumable not found'}), 404
        return jsonify(item)

    except Exception as e:
        print(f"❌ Error fetching consumable by ID: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        conn.close()

# ✅ Bulk Update Consumables
@manage_consumable_bp.route('/consumable/bulk-update', methods=['POST'])
def bulk_update_consumables():
    conn = get_db_connection()
    try:
        data = request.get_json()
        consumable_ids = data.get('consumable_ids', [])
        new_status = data.get('new_status')
        
        if not consumable_ids or not new_status:
            return jsonify({'success': False, 'error': 'Missing required parameters'})
        
        with conn.cursor() as cur:
            placeholders = ','.join(['%s'] * len(consumable_ids))
            cur.execute(f"""
                UPDATE devices_full 
                SET status = %s 
                WHERE accession_id IN ({placeholders}) AND device_type = 'Consumable'
            """, [new_status] + consumable_ids)
            conn.commit()
            
        return jsonify({'success': True, 'message': f'Updated {len(consumable_ids)} consumables'})
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error bulk updating consumables: {e}")
        return jsonify({'success': False, 'error': 'Bulk update failed'})
    finally:
        conn.close()

# ✅ Bulk Mark Checked
@manage_consumable_bp.route('/consumable/bulk-check', methods=['POST'])
def bulk_mark_checked():
    conn = get_db_connection()
    try:
        data = request.get_json()
        consumable_ids = data.get('consumable_ids', [])
        
        if not consumable_ids:
            return jsonify({'success': False, 'error': 'Missing consumable IDs'})
        
        with conn.cursor() as cur:
            placeholders = ','.join(['%s'] * len(consumable_ids))
            cur.execute(f"""
                UPDATE devices_full 
                SET last_checked = CURDATE() 
                WHERE accession_id IN ({placeholders}) AND device_type = 'Consumable'
            """, consumable_ids)
            conn.commit()
            
        return jsonify({'success': True, 'message': f'Marked {len(consumable_ids)} consumables as checked'})
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error bulk marking consumables: {e}")
        return jsonify({'success': False, 'error': 'Bulk check failed'})
    finally:
        conn.close()

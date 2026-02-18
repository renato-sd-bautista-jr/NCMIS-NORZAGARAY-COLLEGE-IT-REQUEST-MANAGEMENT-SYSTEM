from db import get_db_connection
import pymysql
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import qrcode, os
import time,random

manage_item_bp = Blueprint('manage_item_bp', __name__, template_folder='templates')


# ✅ Get Devices with Departments
@manage_item_bp.route('/get-devices-with-details')
def get_devices_with_details():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    df.accession_id,
                    df.item_name,
                    df.brand_model,
                    df.serial_no,
                    df.municipal_serial_no,
                    df.quantity,
                    df.device_type,
                    df.acquisition_cost,
                    df.date_acquired,
                    df.accountable,
                    df.status AS unit_status,
                    df.maintenance_interval_days,
                    df.last_checked,
                    dep.department_id,
                    dep.department_name
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                ORDER BY df.accession_id
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching devices_full: {e}")
        return []
    finally:
        conn.close()


# ✅ Fetch Departments
@manage_item_bp.route('/get-departments')
def get_departments():
    conn = get_db_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
        results = cur.fetchall()
    conn.close()
    return jsonify(results)


@manage_item_bp.route('/add-device', methods=['POST'])
def add_device():
    conn = get_db_connection()
    try:
        form = request.form
        item_name = form.get('item_name')
        brand_model = form.get('brand_model')
        device_type = form.get('device_type')
        acquisition_cost = form.get('acquisition_cost')
        date_acquired = form.get('date_acquired')
        accountable = form.get('accountable')
        department_id = form.get('department_id')
        status = form.get('status') or 'Available'
        quantity = int(form.get('quantity', 1))
        maintenance_interval_days = int(form.get('maintenance_interval_days', 30))

        inserted_ids = []

        with conn.cursor() as cur:
            is_consumable = (device_type or '').strip().lower() == 'consumable'
            insert_count = 1 if is_consumable else quantity

            for _ in range(insert_count):
                # Auto-generate serials
                serial_no = generate_unique_serial("SN")
                municipal_serial_no = generate_unique_serial("MSN")

                # Ensure uniqueness in DB
                while True:
                    cur.execute("""
                        SELECT COUNT(*) AS count FROM devices_full
                        WHERE serial_no=%s OR municipal_serial_no=%s
                    """, (serial_no, municipal_serial_no))
                    if cur.fetchone()['count'] == 0:
                        break
                    serial_no = generate_unique_serial("SN")
                    municipal_serial_no = generate_unique_serial("MSN")

                cur.execute("""
                    INSERT INTO devices_full (
                        item_name, brand_model, serial_no, municipal_serial_no, quantity,
                        device_type, acquisition_cost, date_acquired, accountable,
                        department_id, status, maintenance_interval_days
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    item_name, brand_model, serial_no, municipal_serial_no,
                    quantity if is_consumable else 1,
                    device_type, acquisition_cost, date_acquired, accountable,
                    department_id, status, maintenance_interval_days
                ))
                inserted_ids.append(cur.lastrowid)

        conn.commit()
        flash(f"{quantity} device(s) added successfully!", "success")
        return redirect(url_for('manage_inventory.inventory_load'))
    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding device: {e}")
        flash("Error adding device.", "danger")
        return redirect(url_for('manage_inventory.inventory_load'))
    finally:
        conn.close()

@manage_item_bp.route('/update-device', methods=['POST'])
def update_device():
    conn = get_db_connection()
    try:
        form = request.form
        accession_id = form.get('accession_id')
        if not accession_id:
            flash("Missing device ID.", "danger")
            return redirect(url_for('manage_inventory.inventory_load'))

        with conn.cursor() as cur:
            # Check for duplicates before updating
            cur.execute("""
                SELECT COUNT(*) AS count FROM devices_full
                WHERE (serial_no=%s OR municipal_serial_no=%s) AND accession_id != %s
            """, (form.get('serial_no'), form.get('municipal_serial_no'), accession_id))
            if cur.fetchone()['count'] > 0:
                flash("Serial No or Municipal Serial No already exists!", "danger")
                return redirect(url_for('manage_inventory.inventory_load'))

            cur.execute("""
                UPDATE devices_full
                SET item_name=%s,
                    brand_model=%s,
                    serial_no=%s,
                    municipal_serial_no=%s,
                    device_type=%s,
                    acquisition_cost=%s,
                    date_acquired=%s,
                    accountable=%s,
                    quantity=%s,
                    department_id=%s,
                    status=%s,
                    maintenance_interval_days=%s
                WHERE accession_id=%s
            """, (
                form.get('item_name'),
                form.get('brand_model'),
                form.get('serial_no'),
                form.get('municipal_serial_no'),
                form.get('device_type'),
                form.get('acquisition_cost'),
                form.get('date_acquired'),
                form.get('accountable'),
                form.get('quantity', 1),
                form.get('department_id'),
                form.get('status'),
                form.get('maintenance_interval_days', 30),
                accession_id
            ))
            conn.commit()
        flash("Device updated successfully!", "success")
        return redirect(url_for('manage_inventory.inventory_load'))
    except Exception as e:
        conn.rollback()
        print(f"❌ Error updating device: {e}")
        flash("Error updating device.", "danger")
        return redirect(url_for('manage_inventory.inventory_load'))
    finally:
        conn.close()

# ✅ Delete Device
@manage_item_bp.route('/delete-item/<int:id>', methods=['POST'])
def delete_item(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM devices_full WHERE accession_id = %s", (id,))
            conn.commit()
        flash("Device deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting device: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('manage_inventory.inventory_load'))


# ✅ Get Item by ID
@manage_item_bp.route('/get-item-by-id/<int:item_id>')
def get_item_by_id(item_id):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    df.accession_id,
                    df.item_name,
                    df.brand_model,
                    df.serial_no,
                    df.municipal_serial_no,
                    df.quantity,
                    df.device_type,
                    df.acquisition_cost,
                    df.date_acquired,
                    df.accountable,
                    df.status,
                    df.maintenance_interval_days,
                    dep.department_id,
                    dep.department_name
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                WHERE df.accession_id = %s
            """, (item_id,))
            item = cur.fetchone()

        if not item:
            return jsonify({'error': 'Item not found'}), 404
        return jsonify(item)

    except Exception as e:
        print(f"❌ Error fetching item by ID: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        conn.close()


# ✅ Check if serial_no or municipal_serial_no already exists
@manage_item_bp.route('/check-serial-duplicate')
def check_serial_duplicate():
    serial_no = request.args.get('serial_no', '').strip()
    municipal_serial_no = request.args.get('municipal_serial_no', '').strip()
    accession_id = request.args.get('accession_id')  # optional for edit mode

    if not serial_no and not municipal_serial_no:
        return jsonify({'duplicate': False})  # return valid JSON even if empty

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = """
                SELECT COUNT(*) AS count FROM devices_full
                WHERE (serial_no=%s OR municipal_serial_no=%s)
            """
            params = [serial_no, municipal_serial_no]
            if accession_id:
                query += " AND accession_id != %s"
                params.append(accession_id)

            cur.execute(query, params)
            result = cur.fetchone()
            duplicate = result['count'] > 0
        return jsonify({"duplicate": duplicate})
    finally:
        conn.close()

def generate_unique_serial(prefix="SN"):
    """Generate a unique serial number"""
    return f"{prefix}{int(time.time()*1000) % 1000000}{random.randint(10,99)}"


@manage_item_bp.route('/filter-device', methods=['GET'])
def filter_devices():
    """Filter devices dynamically based on query parameters."""
    conn = get_db_connection()
    try:
        # Get all possible query parameters
        department_id = request.args.get('department_id')
        status = request.args.get('status')
        location = request.args.get('location')
        accountable = request.args.get('accountable')
        serial_no = request.args.get('serial_no')
        item_name = request.args.get('item_name')
        brand_model = request.args.get('brand_model')
        device_type = request.args.get('device_type')
        quantity = request.args.get('quantity')
        acquisition_cost = request.args.get('acquisition_cost')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        query = """
            SELECT 
                df.accession_id,
                df.item_name,
                df.brand_model,
                df.serial_no,
                df.municipal_serial_no,
                df.quantity,
                df.device_type,
                df.acquisition_cost,
                df.date_acquired,
                df.accountable,
                df.status,
                df.risk_level,
                df.health_score,
                dep.department_id,
                dep.department_name
            FROM devices_full df
            LEFT JOIN departments dep ON df.department_id = dep.department_id
            WHERE 1=1
        """
        params = []

        # Apply filters dynamically
        if department_id:
            query += " AND df.department_id = %s"
            params.append(department_id)
        if status:
            query += " AND df.status = %s"
            params.append(status)
        if location:
            query += " AND df.location LIKE %s"
            params.append(f"%{location}%")
        if accountable:
            query += " AND df.accountable LIKE %s"
            params.append(f"%{accountable}%")
        if serial_no:
            query += " AND (df.serial_no LIKE %s OR df.municipal_serial_no LIKE %s)"
            params.extend([f"%{serial_no}%", f"%{serial_no}%"])
        if item_name:
            query += " AND df.item_name LIKE %s"
            params.append(f"%{item_name}%")
        if brand_model:
            query += " AND df.brand_model LIKE %s"
            params.append(f"%{brand_model}%")
        if device_type:
            query += " AND df.device_type LIKE %s"
            params.append(f"%{device_type}%")
        if quantity:
            query += " AND df.quantity = %s"
            params.append(quantity)
        if acquisition_cost:
            query += " AND df.acquisition_cost = %s"
            params.append(acquisition_cost)

        if date_from and date_to:
            query += " AND df.date_acquired BETWEEN %s AND %s"
            params.extend([date_from, date_to])

        query += " ORDER BY df.accession_id"

        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(query, params)
            devices = cur.fetchall()

        return jsonify(devices)

    except Exception as e:
        print(f"❌ Error filtering devices: {e}")
        return jsonify({"error": "Error filtering devices."}), 500
    finally:
        conn.close()


@manage_item_bp.route('/device-filter-modal')
def device_filter_modal():
    departments = get_departments()
    return render_template('partials/filter_device_modal.html', departments=departments)

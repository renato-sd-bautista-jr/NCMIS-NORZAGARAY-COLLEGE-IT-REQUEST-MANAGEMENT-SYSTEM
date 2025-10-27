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

        inserted_ids = []

        with conn.cursor() as cur:
            for _ in range(quantity):
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
                        department_id, status
                    ) VALUES (%s,%s,%s,%s,1,%s,%s,%s,%s,%s,%s)
                """, (
                    item_name, brand_model, serial_no, municipal_serial_no,
                    device_type, acquisition_cost, date_acquired, accountable,
                    department_id, status
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
                    department_id=%s,
                    status=%s
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
                form.get('department_id'),
                form.get('status'),
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
from db import get_db_connection
import pymysql
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
manage_item_bp = Blueprint('manage_item_bp', __name__, template_folder='templates')



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
                    df.serial_number,
                    df.quantity,
                    df.device_type,
                    df.status AS unit_status,
                    dep.department_id,
                    dep.department_name
                FROM devices_full df
                LEFT JOIN departments dep 
                    ON df.department_id = dep.department_id
                ORDER BY df.accession_id
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching devices_full: {e}")
        return []
    finally:
        conn.close()



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
    import qrcode
    import os

    conn = get_db_connection()
    try:
        item_name = request.form.get('item_name')
        brand_model = request.form.get('brand_model')
        serial_number = request.form.get('serial_number')
        quantity = int(request.form.get('quantity', 1))
        device_type = request.form.get('device_type')
        department_id = request.form.get('department_id')
        status = request.form.get('status', 'Available')

        with conn.cursor() as cur:
            # Insert device
            cur.execute("""
                INSERT INTO devices_full 
                (item_name, brand_model, serial_number, quantity, device_type, department_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (item_name, brand_model, serial_number, quantity, device_type, department_id, status))
            
            conn.commit()

            # ✅ Get ID directly from cursor (more reliable than LAST_INSERT_ID)
            accession_id = cur.lastrowid
            print(f"✅ New accession_id: {accession_id}")

        # ✅ Generate the QR code image
        qr_data = f"http://localhost:5000/device/{accession_id}"
        qr_img = qrcode.make(qr_data)

        # ✅ Ensure directory exists
        qr_folder = os.path.join('static', 'device_qr')
        os.makedirs(qr_folder, exist_ok=True)

        # ✅ Save QR code as PNG
        qr_path = os.path.join(qr_folder, f"{accession_id}.png")
        qr_img.save(qr_path)
        print(f"✅ QR saved at: {qr_path}")

        flash("Device added successfully with QR code!", "success")
        return redirect(url_for('inventory_bp.inventory_page'))

    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding device: {str(e)}")
        flash("Error adding device. Please try again.", "danger")
        return redirect(url_for('inventory_bp.inventory_page'))
    finally:
        conn.close()

@manage_item_bp.route('/delete-item/<int:id>', methods=['POST'])
def delete_item(id):
    """Deletes a device from devices_full by accession_id."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if item exists
            cur.execute("SELECT * FROM devices_full WHERE accession_id = %s", (id,))
            result = cur.fetchone()

            if not result:
                flash("Item not found.", "danger")
                return redirect(url_for('inventory_bp.inventory_page'))
            # Delete the record
            cur.execute("DELETE FROM devices_full WHERE accession_id = %s", (id,))
            conn.commit()

        flash("Device deleted successfully!", "success")
        return redirect(url_for('inventory_bp.inventory_page'))

    except Exception as e:
        conn.rollback()
        print(f"❌ Error deleting device: {e}")
        flash("Error deleting device. Please try again.", "danger")

    finally:
        conn.close()


@manage_item_bp.route('/edit-item/<int:id>', methods=['POST'])
def edit_item(id):
    conn = get_db_connection()
    form = request.form

    try:
        with conn.cursor() as cur:
            # quantity excluded from update
            cur.execute("""
                UPDATE devices_full
                SET item_name = %s,
                    brand_model = %s,
                    serial_number = %s,
                    device_type = %s,
                    department_id = %s,
                    status = %s
                WHERE accession_id = %s
            """, (
                form['item_name'],
                form['brand_model'],
                form['serial_number'],
                form['device_type'],
                form['department_id'],
                form['status'],
                id
            ))
            conn.commit()

        flash('Item updated successfully!', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Error updating item: {str(e)}', 'danger')

    finally:
        conn.close()

    return redirect(url_for('inventory_bp.inventory_page'))


@manage_item_bp.route('/update-device', methods=['POST'])
def update_device():
    """Update an existing device in devices_full."""
    conn = get_db_connection()
    try:
        accession_id = request.form.get('accession_id')
        item_name = request.form.get('item_name')
        brand_model = request.form.get('brand_model')
        serial_number = request.form.get('serial_number')
        device_type = request.form.get('device_type')
        department_id = request.form.get('department_id')
        status = request.form.get('status')

        if not accession_id:
            flash("Missing device ID.", "danger")
            return redirect(url_for('inventory_bp.inventory_page'))

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE devices_full
                SET 
                    item_name = %s,
                    brand_model = %s,
                    serial_number = %s,
                    device_type = %s,
                    department_id = %s,
                    status = %s
                WHERE accession_id = %s
            """, (
                item_name,
                brand_model,
                serial_number,
                device_type,
                department_id,
                status,
                accession_id
            ))
            conn.commit()

        flash("Device updated successfully!", "success")
        return redirect(url_for('inventory_bp.inventory_page'))

    except Exception as e:
        conn.rollback()
        print(f"❌ Error updating device: {str(e)}")
        flash("Error updating device. Please try again.", "danger")
        return redirect(url_for('manage_inventory.inventory_load'))

    finally:
        conn.close()
@manage_item_bp.route('/get-item-by-id/<int:item_id>')
def get_item_by_id(item_id):
    """Fetch a single item (device) by its accession_id with department details."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    df.accession_id AS id,
                    df.item_name AS name,
                    df.brand_model,
                    df.serial_number,
                    df.quantity,
                    df.device_type AS category,
                    df.status,
                    df.note,
                    dep.department_id,
                    dep.department_name
                FROM devices_full df
                LEFT JOIN departments dep 
                    ON df.department_id = dep.department_id
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

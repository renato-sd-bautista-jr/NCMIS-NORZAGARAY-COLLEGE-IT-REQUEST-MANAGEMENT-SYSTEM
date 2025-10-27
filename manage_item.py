from db import get_db_connection
import pymysql
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import qrcode, os

manage_item_bp = Blueprint('manage_item_bp', __name__, template_folder='templates')


# ✅ Get Devices with Departments
@manage_item_bp.route('/get-devices', methods=['GET'])
def get_devices():
    """
    Fetch devices from devices_full with optional filters:
    name, brand/model, serial, municipal serial, acquisition cost, date, accountable, department, status
    Returns JSON to be used in the current table.
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Get filters from query params
    name = request.args.get('name', '').strip()
    brand = request.args.get('brand', '').strip()
    serial = request.args.get('serial', '').strip()
    municipal_serial = request.args.get('municipal_serial', '').strip()
    acquisition_cost = request.args.get('acquisition_cost', '').strip()
    date_acquired = request.args.get('date_acquired', '').strip()
    accountable = request.args.get('accountable', '').strip()
    department = request.args.get('department', '').strip()
    status = request.args.get('status', '').strip()

    query = """
        SELECT 
            df.accession_id,
            df.item_name,
            df.brand_model,
            df.serial_no,
            df.municipal_serial_no,
            df.acquisition_cost,
            df.date_acquired,
            df.accountable,
            df.status,
            dep.department_name
        FROM devices_full df
        LEFT JOIN departments dep ON df.department_id = dep.department_id
        WHERE 1=1
    """

    filters = []
    params = []

    if name:
        filters.append("df.item_name LIKE %s")
        params.append(f"%{name}%")
    if brand:
        filters.append("df.brand_model LIKE %s")
        params.append(f"%{brand}%")
    if serial:
        filters.append("df.serial_no LIKE %s")
        params.append(f"%{serial}%")
    if municipal_serial:
        filters.append("df.municipal_serial_no LIKE %s")
        params.append(f"%{municipal_serial}%")
    if acquisition_cost:
        filters.append("df.acquisition_cost = %s")
        params.append(acquisition_cost)
    if date_acquired:
        filters.append("df.date_acquired = %s")
        params.append(date_acquired)
    if accountable:
        filters.append("df.accountable LIKE %s")
        params.append(f"%{accountable}%")
    if department and department.lower() != 'all':
        filters.append("dep.department_id = %s")
        params.append(department)
    if status and status.lower() != 'all':
        filters.append("df.status = %s")
        params.append(status)

    if filters:
        query += " AND " + " AND ".join(filters)

    query += " ORDER BY df.accession_id DESC"

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(data)

# ✅ Fetch Departments
@manage_item_bp.route('/get-departments')
def get_departments():
    conn = get_db_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
        results = cur.fetchall()
    conn.close()
    return jsonify(results)


# ✅ Add Device
@manage_item_bp.route('/add-device', methods=['POST'])
def add_device():
    conn = get_db_connection()
    try:
        form = request.form
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO devices_full (
                    item_name, brand_model, serial_no, municipal_serial_no, quantity,
                    device_type, acquisition_cost, date_acquired, accountable,
                    department_id, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                form.get('item_name'),
                form.get('brand_model'),
                form.get('serial_no'),
                form.get('municipal_serial_no'),
                int(form.get('quantity', 1)),
                form.get('device_type'),
                form.get('acquisition_cost'),
                form.get('date_acquired'),
                form.get('accountable'),
                form.get('department_id'),
                form.get('status', 'Available')
            ))
            conn.commit()
            accession_id = cur.lastrowid

        # ✅ Generate QR Code
        qr_data = f"http://localhost:5000/device/{accession_id}"
        qr_img = qrcode.make(qr_data)
        qr_folder = os.path.join('static', 'device_qr')
        os.makedirs(qr_folder, exist_ok=True)
        qr_img.save(os.path.join(qr_folder, f"{accession_id}.png"))

        flash("Device added successfully with QR code!", "success")
        return redirect(url_for('manage_inventory.inventory_load'))

    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding device: {e}")
        flash("Error adding device.", "danger")
        return redirect(url_for('manage_inventory.inventory_load'))
    finally:
        conn.close()

@manage_item_bp.route('/filter-devices', methods=['POST'])
def filter_devices():
    db = get_db_connection()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT i.*, d.department_name
        FROM devices_full i
        LEFT JOIN departments d ON i.department_id = d.department_id
        WHERE 1=1
    """
    filters = []
    data = request.form

    if data.get('item_name'):
        query += " AND i.item_name LIKE %s"
        filters.append(f"%{data['item_name']}%")

    if data.get('brand_model'):
        query += " AND i.brand_model LIKE %s"
        filters.append(f"%{data['brand_model']}%")

    if data.get('serial_no'):
        query += " AND i.serial_no LIKE %s"
        filters.append(f"%{data['serial_no']}%")

    if data.get('municipal_serial_no'):
        query += " AND i.municipal_serial_no LIKE %s"
        filters.append(f"%{data['municipal_serial_no']}%")

    if data.get('acquisition_cost'):
        query += " AND i.acquisition_cost = %s"
        filters.append(data['acquisition_cost'])

    if data.get('date_acquired'):
        query += " AND i.date_acquired = %s"
        filters.append(data['date_acquired'])

    if data.get('accountable'):
        query += " AND i.accountable LIKE %s"
        filters.append(f"%{data['accountable']}%")

    if data.get('department_id') and data['department_id'] != 'all':
        query += " AND i.department_id = %s"
        filters.append(data['department_id'])

    if data.get('status') and data['status'] != 'all':
        query += " AND i.status = %s"
        filters.append(data['status'])

    cursor.execute(query, tuple(filters))
    item_list = cursor.fetchall()
    cursor.close()
    db.close()

    # Render the table rows directly
    table_rows = ""
    for item in item_list:
        status_class = (
            "text-green-600" if item['status'] == 'Available' else
            "text-blue-600" if item['status'] == 'In Used' else
            "text-gray-500" if item['status'] == 'Inactive' else
            "text-red-600"
        )

        table_rows += f"""
        <tr class="hover:bg-gray-100 transition">
            <td class="px-4 py-2 border-b">{item['item_name']}</td>
            <td class="px-4 py-2 border-b">{item.get('brand_model', '—')}</td>
            <td class="px-4 py-2 border-b">{item.get('serial_no', '—')}</td>
            <td class="px-4 py-2 border-b">{item.get('municipal_serial_no', '—')}</td>
            <td class="px-4 py-2 border-b">₱{item.get('acquisition_cost', 0):.2f}</td>
            <td class="px-4 py-2 border-b">{item.get('date_acquired', '—')}</td>
            <td class="px-4 py-2 border-b">{item.get('accountable', '—')}</td>
            <td class="px-4 py-2 border-b">{item.get('department_name', '—')}</td>
            <td class="px-4 py-2 border-b"><span class="{status_class} font-medium">{item['status']}</span></td>
            <td class="px-4 py-2 border-b flex gap-2">
                <button onclick="openItemModalById({item['accession_id']})"
                    class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs shadow">
                    Edit
                </button>
                <button type="button"
                    onclick="openDeleteModal('{url_for('manage_item_bp.delete_item', id=item['accession_id'])}')"
                    class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs shadow">
                    Delete
                </button>
            </td>
        </tr>
        """

    return table_rows


# ✅ Update Device
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
            cur.execute("""
                UPDATE devices_full
                SET item_name = %s,
                    brand_model = %s,
                    serial_no = %s,
                    municipal_serial_no = %s,
                    device_type = %s,
                    acquisition_cost = %s,
                    date_acquired = %s,
                    accountable = %s,
                    department_id = %s,
                    status = %s
                WHERE accession_id = %s
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


@manage_item_bp.route('/batch_add_devices', methods=['POST'])
def batch_add_devices():
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({'success': False, 'error': 'Invalid data format'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            inserted = 0

            # 🔹 Department info
            first_device = data[0]
            department_id = first_device.get('department_id')
            if not department_id:
                return jsonify({'success': False, 'error': 'Missing department ID'}), 400

            # 🔹 Get department code
            cur.execute("SELECT department_name, department_code FROM departments WHERE department_id = %s", (department_id,))
            dept_row = cur.fetchone()
            if not dept_row:
                return jsonify({'success': False, 'error': 'Department not found'}), 404

            dept_code = (dept_row['department_code'] or dept_row['department_name']).strip().lower().replace(' ', '-')

            # 🔹 Determine base name (e.g., "printer-clc")
            base_name = first_device.get('item_name', 'device').strip().lower().replace(' ', '-')
            full_prefix = f"{base_name}-{dept_code}"

            # 🔹 Find existing names to continue numbering
            cur.execute("SELECT item_name FROM devices_full WHERE department_id = %s AND item_name LIKE %s",
                        (department_id, f"{full_prefix}-%"))
            existing_names = [row['item_name'] for row in cur.fetchall()]

            # Find the max numeric suffix
            import re
            max_num = 0
            pattern = re.compile(rf"^{re.escape(full_prefix)}-(\d+)$")
            for name in existing_names:
                match = pattern.match(name)
                if match:
                    max_num = max(max_num, int(match.group(1)))

            next_num = max_num + 1

            # 🔹 Generate new devices
            for dev in data:
                dev['item_name'] = f"{full_prefix}-{next_num:02d}"
                next_num += 1

                # Auto-generate unique serials
                import random, time
                timestamp = str(int(time.time() * 1000))
                rand_suffix = str(random.randint(100000, 999999))
                dev['serial_no'] = f"SN-{timestamp}-{rand_suffix}"
                dev['municipal_serial_no'] = f"MSN-{timestamp}-{random.randint(100000, 999999)}"

                # Default values if missing
                dev.setdefault('quantity', 1)
                dev.setdefault('status', 'Available')

                cur.execute("""
                    INSERT INTO devices_full (
                        item_name, brand_model, serial_no, municipal_serial_no,
                        quantity, device_type, acquisition_cost, date_acquired, accountable,
                        department_id, status, created_at, updated_at
                    ) VALUES (
                        %(item_name)s, %(brand_model)s, %(serial_no)s, %(municipal_serial_no)s,
                        %(quantity)s, %(device_type)s, %(acquisition_cost)s, %(date_acquired)s, %(accountable)s,
                        %(department_id)s, %(status)s, NOW(), NOW()
                    )
                """, dev)
                inserted += 1

        conn.commit()
        return jsonify({
            'success': True,
            'message': f"Successfully added {inserted} devices under {dept_row['department_name']} ({dept_code.upper()})"
        })

    except Exception as e:
        conn.rollback()
        print(f"❌ Batch add error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

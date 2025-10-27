from flask import Blueprint, render_template, flash, jsonify,request
from db import get_db_connection
import pymysql

manage_inventory_bp = Blueprint('manage_inventory', __name__, template_folder='templates', url_prefix='/manage_inventory')


@manage_inventory_bp.route('/manage_inventory')
def inventory_load():
    """Load the Manage Inventory page with PCs and Devices."""
    pc_list = get_pc_list()
    item_list = get_item_list()

    if pc_list is None or item_list is None:
        flash("Error loading data. Please try again.", "danger")

    return render_template('manage_inventory.html', pc_list=pc_list, item_list=item_list)


@manage_inventory_bp.route('/manage_inventory/get-departments')
def get_departments():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT department_id, department_name 
                FROM departments 
                ORDER BY department_name
            """)
            departments = cur.fetchall()
        return jsonify(departments)
    except Exception as e:
        print(f"❌ Error fetching departments: {e}")
        return jsonify([]), 500
    finally:
        conn.close()


def get_pc_list():
    """Fetch all PCs with department and part details from pcinfofull."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    p.pcid,
                    p.pcname,
                    p.department_id,
                    d.department_name,
                    p.location,
                    p.quantity,
                    p.acquisition_cost,
                    p.date_acquired,
                    p.accountable,
                    p.serial_no,
                    p.municipal_serial_no,
                    p.status,
                    p.note,
                    p.monitor,
                    p.motherboard,
                    p.ram,
                    p.storage,
                    p.gpu,
                    p.psu,
                    p.casing,
                    p.other_parts
                FROM pcinfofull p
                LEFT JOIN departments d ON p.department_id = d.department_id
                ORDER BY p.pcid
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Error fetching PC list: {e}")
        return []
    finally:
        conn.close()

@manage_inventory_bp.route('/filter-pcs', methods=['POST'])
def filter_pcs():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    query = """
        SELECT 
            p.pcid,
            p.pcname,
            p.department_id,
            d.department_name,
            p.location,
            p.quantity,
            p.acquisition_cost,
            p.date_acquired,
            p.accountable,
            p.serial_no,
            p.municipal_serial_no,
            p.status,
            p.note

        FROM pcinfofull p
        LEFT JOIN departments d ON p.department_id = d.department_id
        WHERE 1=1
    """

    filters = []
    data = request.form

    if data.get('pcid'):
        query += " AND p.pcid = %s"
        filters.append(data['pcid'])

    if data.get('pcname'):
        query += " AND p.pcname LIKE %s"
        filters.append(f"%{data['pcname']}%")

    if data.get('department_id') and data['department_id'] != 'all':
        query += " AND p.department_id = %s"
        filters.append(data['department_id'])

    if data.get('location'):
        query += " AND p.location LIKE %s"
        filters.append(f"%{data['location']}%")

    if data.get('quantity'):
        query += " AND p.quantity = %s"
        filters.append(data['quantity'])

    if data.get('acquisition_cost'):
        query += " AND p.acquisition_cost = %s"
        filters.append(data['acquisition_cost'])

    if data.get('date_acquired'):
        query += " AND p.date_acquired = %s"
        filters.append(data['date_acquired'])

    if data.get('accountable'):
        query += " AND p.accountable LIKE %s"
        filters.append(f"%{data['accountable']}%")

    if data.get('serial_no'):
        query += " AND p.serial_no LIKE %s"
        filters.append(f"%{data['serial_no']}%")

    if data.get('municipal_serial_no'):
        query += " AND p.municipal_serial_no LIKE %s"
        filters.append(f"%{data['municipal_serial_no']}%")

    if data.get('status') and data['status'] != 'all':
        query += " AND p.status = %s"
        filters.append(data['status'])

    if data.get('note'):
        query += " AND p.note LIKE %s"
        filters.append(f"%{data['note']}%")
    
    query += " ORDER BY p.pcid"

    cursor.execute(query, tuple(filters))
    pc_list = cursor.fetchall()
    cursor.close()
    conn.close()

    # Return table rows only
    return jsonify(pc_list)



def get_item_list():
    """Fetch all devices from devices_full (for Manage Items section)."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    df.accession_id AS accession_id,
                    df.item_name,
                    df.brand_model,
                    df.serial_no,
                    df.municipal_serial_no,
                    df.quantity,
                    df.device_type,
                    df.acquisition_cost,
                    df.date_acquired,
                    df.accountable,
                    df.department_id,
                    dep.department_name,
                    df.status,
                    df.updated_at
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                ORDER BY df.accession_id DESC
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Error fetching item list: {e}")
        return []
    finally:
        conn.close()

@manage_inventory_bp.route('get-item-by-id/<int:item_id>')
def get_item_by_id(item_id):
    """Fetch a single device record with full details."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    df.accession_id AS accession_id,
                    df.item_name,
                    df.brand_model,
                    df.serial_no,
                    df.municipal_serial_no,
                    df.quantity,
                    df.device_type,
                    df.acquisition_cost,
                    df.date_acquired,
                    df.accountable,
                    df.department_id,
                    dep.department_name,
                    df.status,
                    df.updated_at
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


@manage_inventory_bp.route('get-pc-by-id/<int:pcid>')
def get_pc_by_id(pcid):

    
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    p.pcid,
                    p.pcname,
                    p.department_id,
                    d.department_name,
                    p.location,
                    p.quantity,
                    p.acquisition_cost,
                    p.date_acquired,
                    p.accountable,
                    p.serial_no,
                    p.municipal_serial_no,
                    p.status,
                    p.note,
                    p.monitor,
                    p.motherboard,
                    p.ram,
                    p.storage,
                    p.gpu,
                    p.psu,
                    p.casing,
                    p.other_parts
                FROM pcinfofull p
                LEFT JOIN departments d ON p.department_id = d.department_id
                WHERE p.pcid = %s
            """, (pcid,))
            pc = cur.fetchone()

            if not pc:
                return {"error": "PC not found"}, 404

            return pc
    except Exception as e:
        print(f"❌ Error fetching PC by ID: {e}")
        return {"error": "Database error"}, 500
    finally:
        conn.close()


@manage_inventory_bp.route('/manage_inventory/pc-filter-modal')
def pc_filter_modal():
    return render_template('pcFilterModal.html')

@manage_inventory_bp.route('/manage_inventory/device-filter-modal')
def device_filter_modal():
    return render_template('itemfiltermodal.html')    


@manage_inventory_bp.route('/pc-edit-modal')
def open_pc_edit_modal():
        return render_template('pceditmodal.html')

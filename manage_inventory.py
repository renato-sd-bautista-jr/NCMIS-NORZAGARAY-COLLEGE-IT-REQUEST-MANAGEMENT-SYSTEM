from flask import Blueprint, render_template, flash, jsonify,request
from db import get_db_connection
import pymysql
from inventory_auto_check import run_inventory_auto_check

 

 

manage_inventory_bp = Blueprint('manage_inventory', __name__, template_folder='templates')


@manage_inventory_bp.route('/manage_inventory')
def inventory_load():
    """Load Manage Inventory with pagination for devices."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    section = request.args.get("section", "pc")
    
    # Get filter parameters
    department_id = request.args.get('department_id')
    status = request.args.get('status')
    accountable = request.args.get('accountable')
    serial_no = request.args.get('serial_no')
    item_name = request.args.get('item_name')
    brand_model = request.args.get('brand_model')
    device_type = request.args.get('device_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # PCs
    pc_list, pc_total, pc_pages = get_pc_list_paginated(page, per_page)
    
    # Check if we have filter parameters for devices
    if any([department_id, status, accountable, serial_no, item_name, brand_model, device_type, date_from, date_to]):
        item_list, item_total, item_pages = get_filtered_item_list_paginated(
            page, per_page, department_id, status, accountable, serial_no, 
            item_name, brand_model, device_type, date_from, date_to
        )
    else:
        item_list, item_total, item_pages = get_item_list_paginated(page, per_page)
     
    # Load consumables
    consumables = get_consumables_list()
    
    # Load departments for filters
    departments = get_departments_list()
     
    if pc_list is None or item_list is None:
        flash("Error loading data. Please try again.", "danger")

    return render_template(
        'manage_inventory.html',
        pc_list=pc_list,
        item_list=item_list,
        consumables=consumables,
        departments=departments,

        page=page,
        per_page=per_page,
        section=section,

        pc_total_items=pc_total,
        pc_total_pages=pc_pages,

        total_items=item_total,
        total_pages=item_pages
    )

@manage_inventory_bp.route('/manage_inventory/items-paged')
def items_paged():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    items, total_items, total_pages = get_item_list_paginated(page, per_page)

    return jsonify({
        "items": items,
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages
    })
 
@manage_inventory_bp.route('/manage_inventory/pcs-paged')
def pcs_paged():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pcs, total_items, total_pages = get_pc_list_paginated(page, per_page)

    return jsonify({
        "pcs": pcs,
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages
    })
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

@manage_inventory_bp.route('/inventory/pc/bulk-check', methods=['POST'])
def bulk_mark_pc_checked():
    data = request.get_json()
    pcids = data.get("pcids", [])

    if not pcids:
        return jsonify(success=False, error="No PCs selected"), 400

    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:

            for pcid in pcids:
                # Fetch old state
                cur.execute("""
                    SELECT status, risk_level
                    FROM pcinfofull
                    WHERE pcid = %s
                """, (pcid,))
                old = cur.fetchone()

                if not old:
                    continue

                # Update PC
                cur.execute("""
                    UPDATE pcinfofull
                    SET
                        last_checked = CURDATE(),
                        health_score = 100,
                        risk_level = 'Low',
                        status = 'Available'
                    WHERE pcid = %s
                """, (pcid,))

                # Maintenance log
                cur.execute("""
                    INSERT INTO maintenance_logs (
                        asset_type, asset_id,
                        previous_status, new_status,
                        previous_risk_level, new_risk_level,
                        action
                    ) VALUES (
                        'PC', %s,
                        %s, 'Available',
                        %s, 'Low',
                        'Bulk inspection completed'
                    )
                """, (
                    pcid,
                    old['status'],
                    old['risk_level']
                ))

                # Maintenance history
                cur.execute("""
                    INSERT INTO maintenance_history (
                        pcid,
                        asset_type,
                        asset_id,
                        action,
                        old_status,
                        new_status,
                        risk_level,
                        health_score,
                        performed_by,
                        remarks
                    ) VALUES (
                        %s, 'PC', %s,
                        'Bulk inspection completed',
                        %s, 'Available',
                        'Low', 100,
                        %s, %s
                    )
                """, (
                    pcid,
                    pcid,
                    old['status'],
                    'System',
                    'Bulk marked as checked'
                ))

        conn.commit()
        return jsonify(success=True)

    except Exception as e:
        conn.rollback()
        return jsonify(success=False, error=str(e)), 500

    finally:
        conn.close()

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()

@manage_inventory_bp.route('/inventory/device/bulk-update', methods=['POST'])
def bulk_update_devices():
    data = request.get_json()
    device_ids = data.get("device_ids", [])
    new_status = data.get("new_status")

    if not device_ids or not new_status:
        return jsonify(success=False, error="Invalid input"), 400

    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            for accession_id in device_ids:

                # Fetch old state
                cur.execute("""
                    SELECT status, risk_level, health_score
                    FROM devices_full
                    WHERE accession_id = %s
                """, (accession_id,))
                old = cur.fetchone()

                if not old:
                    continue

                # ---- Risk & health rules ----
                risk = old["risk_level"]
                health = old["health_score"]

                if new_status in ("Damaged", "Needs Checking"):
                    risk = "High"
                    health = min(health, 40)
                elif new_status == "Inactive":
                    risk = "Medium"
                    health = min(health, 70)
                elif new_status == "Available":
                    risk = "Low"
                    health = 100

                # ---- Update device ----
                cur.execute("""
                    UPDATE devices_full
                    SET
                        status = %s,
                        risk_level = %s,
                        health_score = %s,
                        updated_at = NOW()
                    WHERE accession_id = %s
                """, (new_status, risk, health, accession_id))

                # ---- maintenance_logs ----
                cur.execute("""
                    INSERT INTO maintenance_logs (
                        asset_type, asset_id,
                        previous_status, new_status,
                        previous_risk_level, new_risk_level,
                        action
                    ) VALUES (
                        'DEVICE', %s,
                        %s, %s,
                        %s, %s,
                        'Bulk status update'
                    )
                """, (
                    accession_id,
                    old["status"],
                    new_status,
                    old["risk_level"],
                    risk
                ))

                # ---- maintenance_history ----
                cur.execute("""
                    INSERT INTO maintenance_history (
                        asset_type,
                        asset_id,
                        action,
                        old_status,
                        new_status,
                        risk_level,
                        health_score,
                        performed_by,
                        remarks
                    ) VALUES (
                        'DEVICE', %s,
                        'Bulk status update',
                        %s, %s,
                        %s, %s,
                        %s,
                        %s
                    )
                """, (
                    accession_id,
                    old["status"],
                    new_status,
                    risk,
                    health,
                    'System',
                    f'Bulk marked as {new_status}'
                ))

        conn.commit()
        return jsonify(success=True)

    except Exception as e:
        conn.rollback()
        return jsonify(success=False, error=str(e)), 500

    finally:
        conn.close()

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
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
                    p.motherboard,
                    p.ram,
                    p.storage,
                    p.gpu,
                    p.psu,
                    p.casing,
                    p.other_parts,
                    p.risk_level,
                    p.health_score
                   
                
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

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()



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
                    df.risk_level,
                    df.health_score,
                    df.last_checked,
                    df.maintenance_interval_days
                    df.note,
                    df.location,
                    df.supplier
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

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()

@manage_inventory_bp.route('/manage_inventory/get-item-by-id/<int:item_id>')
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

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()


@manage_inventory_bp.route('/manage_inventory/get-pc-by-id/<int:pcid>')
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

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()


@manage_inventory_bp.route('/manage_inventory/pc-filter-modal')
def pc_filter_modal():
    return render_template('pcFilterModal.html')
def get_pc_list_paginated(page=1, per_page=10):
    """
    Fetch paginated PCs from pcinfofull.
    Returns:
        pcs, total_items, total_pages
    """
    offset = (page - 1) * per_page
    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Total count
            cur.execute("SELECT COUNT(*) AS total FROM pcinfofull")
            total_items = cur.fetchone()["total"]

            # Paginated PC data
            cur.execute("""
                SELECT
                    pc.pcid,
                    pc.pcname,
                    pc.department_id,
                    dep.department_name,
                    pc.location,
                    pc.acquisition_cost,
                    pc.date_acquired,
                    pc.accountable,
                    pc.serial_no,
                    pc.municipal_serial_no,
                    pc.note,
                    pc.status,
                    pc.last_checked,
                    pc.health_score,
                    pc.risk_level
                FROM pcinfofull pc
                LEFT JOIN departments dep
                    ON pc.department_id = dep.department_id
                ORDER BY pc.pcid DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))

            pcs = cur.fetchall()

        total_pages = (total_items + per_page - 1) // per_page
        return pcs, total_items, total_pages

    except Exception as e:
        print(f"❌ Error fetching paginated PCs: {e}")
        return [], 0, 0

    finally:
        conn.close()

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()
def get_item_list_paginated(page=1, per_page=10):
    """
    Fetch paginated devices from devices_full.
    Returns:
        items, total_items, total_pages
    """
    offset = (page - 1) * per_page
    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Get total count
            cur.execute("SELECT COUNT(*) AS total FROM devices_full")
            total_items = cur.fetchone()["total"]

            # Get paginated data
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
                    df.updated_at,
                    df.risk_level,
                    df.health_score,
                    df.last_checked,
                    df.maintenance_interval_days
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                ORDER BY df.accession_id DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))

            items = cur.fetchall()

        total_pages = (total_items + per_page - 1) // per_page
        return items, total_items, total_pages

    except Exception as e:
        print(f"❌ Error fetching paginated items: {e}")
        return [], 0, 0
    finally:
        conn.close()

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()

def get_filtered_item_list_paginated(page=1, per_page=10, department_id=None, status=None, 
                                   accountable=None, serial_no=None, item_name=None, 
                                   brand_model=None, device_type=None, date_from=None, date_to=None):
    """
    Fetch paginated and filtered devices from devices_full.
    Returns:
        items, total_items, total_pages
    """
    offset = (page - 1) * per_page
    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Build the base query with filters
            query = """
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
                    df.updated_at,
                    df.risk_level,
                    df.health_score,
                    df.last_checked,
                    df.maintenance_interval_days
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
            if date_from and date_to:
                query += " AND df.date_acquired BETWEEN %s AND %s"
                params.extend([date_from, date_to])

            # Get total count with same filters
            count_query = query.replace(
                "SELECT df.accession_id AS accession_id, df.item_name, df.brand_model, df.serial_no, df.municipal_serial_no, df.quantity, df.device_type, df.acquisition_cost, df.date_acquired, df.accountable, df.department_id, dep.department_name, df.status, df.updated_at, df.risk_level, df.health_score, df.last_checked, df.maintenance_interval_days",
                "SELECT COUNT(*) AS total"
            ).replace("ORDER BY df.accession_id DESC", "")
            
            cur.execute(count_query, params)
            total_items = cur.fetchone()["total"]

            # Get paginated data
            query += " ORDER BY df.accession_id DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])

            cur.execute(query, params)
            items = cur.fetchall()

        total_pages = (total_items + per_page - 1) // per_page
        return items, total_items, total_pages

    except Exception as e:
        print(f"❌ Error fetching filtered paginated items: {e}")
        return [], 0, 0

    finally:
        conn.close()

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()

@manage_inventory_bp.route('/manage_inventory/run-risk-update', methods=['POST'])
def run_risk_update():
    

    try:
        run_inventory_auto_check()
        return jsonify({
            "success": True,
            "message": "Inventory risk levels recalculated."
        })
    except Exception as e:
        print("Risk update error:", e)
        return jsonify({
            "success": False,
            "message": "Risk update failed."
        }), 500
    
@manage_inventory_bp.route('/inventory/pc/<int:pcid>/check', methods=['POST'])
def mark_pc_checked(pcid):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT status, risk_level
                FROM pcinfofull
                WHERE pcid = %s
            """, (pcid,))
            old = cur.fetchone()

            cur.execute("""
                UPDATE pcinfofull
                SET
                    last_checked = CURDATE(),
                    health_score = 100,
                    risk_level = 'Low',
                    status = 'Available'
                WHERE pcid = %s
            """, (pcid,))

            cur.execute("""
                INSERT INTO maintenance_logs (
                    asset_type, asset_id,
                    previous_status, new_status,
                    previous_risk_level, new_risk_level,
                    action
                ) VALUES (
                    'PC', %s,
                    %s, 'Available',
                    %s, 'Low',
                    'Manual inspection completed'
                )
            """, (
                pcid,
                old['status'],
                old['risk_level']
            ))
            cur.execute("""
                INSERT INTO maintenance_history (
                    pcid, asset_type, asset_id,
                    action, old_status, new_status,
                    risk_level, health_score, performed_by, remarks
                ) VALUES (
                    %s, 'PC', %s,
                    'Manual inspection completed', %s, 'Available',
                    'Low', 100, %s, %s
                )
            """, (
                pcid,
                pcid,
                old['status'],
                'System',   # you can replace 'System' with current user if available
                'Marked as checked manually'
            ))

        conn.commit()
        return jsonify(success=True)

    except Exception as e:
        conn.rollback()
        return jsonify(success=False, error=str(e)), 500
    finally:
        conn.close()

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()

@manage_inventory_bp.route('/maintenance-history')
def maintenance_history():
    asset_id = request.args.get('id', type=int)
    asset_type = request.args.get('type')

    conn = get_db_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT *
            FROM maintenance_logs
            WHERE asset_type = %s AND asset_id = %s
            ORDER BY performed_at DESC
        """, (asset_type, asset_id))
        logs = cur.fetchall()

    conn.close()
    return render_template('maintenance_history.html', logs=logs)

@manage_inventory_bp.route('/inventory/<string:asset_type>/<int:asset_id>/check', methods=['POST'])
def mark_asset_checked(asset_type, asset_id):
    asset_type = asset_type.upper()
    conn = get_db_connection()

    if asset_type not in ['PC', 'DEVICE']:
        return jsonify(success=False, error="Invalid asset type"), 400

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:

            # ---------- TARGET TABLE ----------
            if asset_type == 'PC':
                table = 'pcinfofull'
                id_field = 'pcid'
            else:
                table = 'devices_full'
                id_field = 'accession_id'

            # ---------- FETCH OLD STATE ----------
            cur.execute(f"""
                SELECT status, risk_level, health_score
                FROM {table}
                WHERE {id_field} = %s
            """, (asset_id,))
            old = cur.fetchone()

            if not old:
                return jsonify(success=False, error="Asset not found"), 404

            # ---------- UPDATE ASSET ----------
            cur.execute(f"""
                UPDATE {table}
                SET
                    last_checked = CURDATE(),
                    health_score = 100,
                    risk_level = 'Low',
                    status = 'Available'
                WHERE {id_field} = %s
            """, (asset_id,))

            # ---------- MAINTENANCE LOG ----------
            cur.execute("""
                INSERT INTO maintenance_logs (
                    asset_type,
                    asset_id,
                    previous_status,
                    new_status,
                    previous_risk_level,
                    new_risk_level,
                    action
                ) VALUES (
                    %s, %s,
                    %s, 'Available',
                    %s, 'Low',
                    'Manual inspection completed'
                )
            """, (
                asset_type,
                asset_id,
                old['status'],
                old['risk_level']
            ))

            # ---------- MAINTENANCE HISTORY ----------
            cur.execute("""
                INSERT INTO maintenance_history (
                    pcid,
                    asset_type,
                    asset_id,
                    action,
                    old_status,
                    new_status,
                    risk_level,
                    health_score,
                    performed_by,
                    remarks
                ) VALUES (
                    %s, %s, %s,
                    'Manual inspection completed',
                    %s,
                    'Available',
                    'Low',
                    100,
                    %s,
                    %s
                )
            """, (
                asset_id if asset_type == 'PC' else None,  # pcid
                asset_type,
                asset_id,                                 # accession_id for DEVICE
                old['status'],
                'System',
                'Marked as checked manually'
            ))

        conn.commit()
        return jsonify(success=True)

    except Exception as e:
        conn.rollback()
        return jsonify(success=False, error=str(e)), 500

    finally:
        conn.close()

def get_consumables_list():
    """Get all consumables with department information."""
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

def get_departments_list():
    """Get all departments for filter dropdowns."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        conn.close()
